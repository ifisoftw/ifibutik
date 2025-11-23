from django.shortcuts import render
from django.db.models import Sum, Count, Avg, F, Q
from django.utils import timezone
from datetime import timedelta, datetime
from orders.models import Order, OrderItem
from campaigns.models import Campaign
from products.models import Product
from admin_panel.decorators import admin_required
import json


@admin_required('view_dashboard')
def dashboard(request):
    """Dashboard ana sayfası"""
    today = timezone.now().date()
    yesterday = today - timedelta(days=1)
    now = timezone.now()
    
    # ====== KPI Metrics ======
    
    # Bugün Ciro
    today_revenue = Order.objects.filter(
        created_at__date=today,
        status__in=['processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Dün Ciro
    yesterday_revenue = Order.objects.filter(
        created_at__date=yesterday,
        status__in=['processing', 'shipped', 'delivered']
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Bugün Ciro değişim yüzdesi
    if yesterday_revenue > 0:
        revenue_change = ((today_revenue - yesterday_revenue) / yesterday_revenue) * 100
    else:
        revenue_change = 100 if today_revenue > 0 else 0
    
    # Son 5 Dakika Satışları
    five_min_ago = now - timedelta(minutes=5)
    last_5_min_sales = Order.objects.filter(
        created_at__gte=five_min_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Aktif Ziyaretçi Sayısı (simulated - gerçekte analytics kullan)
    active_visitors = 2  # Placeholder
    
    # Sepet Ortalaması
    avg_cart = Order.objects.filter(
        created_at__date=today
    ).aggregate(avg=Avg('total_amount'))['avg'] or 0
    
    # ====== Grafik Verileri ======
    
    # Saatlik satış verileri (bugün vs dün)
    hours_today = []
    hours_yesterday = []
    hour_labels = []
    
    for hour in range(24):
        hour_start_today = datetime.combine(today, datetime.min.time()) + timedelta(hours=hour)
        hour_end_today = hour_start_today + timedelta(hours=1)
        
        hour_start_yesterday = datetime.combine(yesterday, datetime.min.time()) + timedelta(hours=hour)
        hour_end_yesterday = hour_start_yesterday + timedelta(hours=1)
        
        # Bugün
        today_hour_total = Order.objects.filter(
            created_at__gte=timezone.make_aware(hour_start_today),
            created_at__lt=timezone.make_aware(hour_end_today)
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        # Dün
        yesterday_hour_total = Order.objects.filter(
            created_at__gte=timezone.make_aware(hour_start_yesterday),
            created_at__lt=timezone.make_aware(hour_end_yesterday)
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        hours_today.append(float(today_hour_total))
        hours_yesterday.append(float(yesterday_hour_total))
        hour_labels.append(f"{hour:02d}:00")
    
    chart_data = {
        'labels': hour_labels,
        'today': hours_today,
        'yesterday': hours_yesterday
    }
    
    # ====== Kampanya Performansı ======
    campaign_performance = Campaign.objects.filter(
        is_active=True
    ).annotate(
        sales_count=Count('order', filter=Q(order__created_at__date=today)),
        yesterday_sales=Count('order', filter=Q(order__created_at__date=yesterday))
    ).order_by('-sales_count')[:5]
    
    # ====== Son Siparişler ======
    recent_orders = Order.objects.select_related(
        'campaign', 'city_fk', 'district_fk'
    ).prefetch_related('items__product').order_by('-created_at')[:10]
    
    # ====== En Çok Satan Ürünler ======
    top_products = Product.objects.annotate(
        sales_count=Count('orderitem', filter=Q(orderitem__order__created_at__date=today))
    ).filter(sales_count__gt=0).order_by('-sales_count')[:5]
    
    # ====== Saatlik Satış Farkı (Table için) ======
    hourly_comparison = []
    for hour in range(24):
        hour_start_today = datetime.combine(today, datetime.min.time()) + timedelta(hours=hour)
        hour_end_today = hour_start_today + timedelta(hours=1)
        
        hour_start_yesterday = datetime.combine(yesterday, datetime.min.time()) + timedelta(hours=hour)
        hour_end_yesterday = hour_start_yesterday + timedelta(hours=1)
        
        today_orders = Order.objects.filter(
            created_at__gte=timezone.make_aware(hour_start_today),
            created_at__lt=timezone.make_aware(hour_end_today)
        ).count()
        
        yesterday_orders = Order.objects.filter(
            created_at__gte=timezone.make_aware(hour_start_yesterday),
            created_at__lt=timezone.make_aware(hour_end_yesterday)
        ).count()
        
        today_total = Order.objects.filter(
            created_at__gte=timezone.make_aware(hour_start_today),
            created_at__lt=timezone.make_aware(hour_end_today)
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        yesterday_total = Order.objects.filter(
            created_at__gte=timezone.make_aware(hour_start_yesterday),
            created_at__lt=timezone.make_aware(hour_end_yesterday)
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        change_percent = 0
        if yesterday_total > 0:
            change_percent = ((today_total - yesterday_total) / yesterday_total) * 100
        elif today_total > 0:
            change_percent = 100
        
        hourly_comparison.append({
            'hour': f"{hour:02d}:00 - {(hour+1):02d}:00",
            'today_orders': today_orders,
            'today_total': today_total,
            'yesterday_orders': yesterday_orders,
            'yesterday_total': yesterday_total,
            'change_percent': change_percent,
            'trend': 'up' if change_percent > 0 else ('down' if change_percent < 0 else 'same')
        })
    
    # ====== Ürün Durumu İstatistikleri ======
    product_stats = {
        'active': Product.objects.filter(is_active=True).count(),
        'passive': Product.objects.filter(is_active=False).count(),
        'with_campaign': Product.objects.filter(campaignproduct__isnull=False).distinct().count(),
        'without_campaign': Product.objects.filter(campaignproduct__isnull=True).count(),
        'multiple_campaigns': Product.objects.annotate(
            campaign_count=Count('campaignproduct')
        ).filter(campaign_count__gt=1).count(),
    }
    
    # ====== Şehir Performansı ======
    city_performance = Order.objects.filter(
        created_at__date__gte=today - timedelta(days=7),
        city_fk__isnull=False
    ).values('city_fk__name').annotate(
        order_count=Count('id'),
        total_revenue=Sum('total_amount')
    ).order_by('-order_count')[:10]
    
    # ====== Beklenen Siparişler ======
    pending_orders_count = Order.objects.filter(status='new').count()
    
    # ====== Missing Metrics for Template ======
    active_campaigns_count = Campaign.objects.filter(is_active=True).count()
    total_orders_today = Order.objects.filter(created_at__date=today).count()

    stats = {
        'today_revenue': today_revenue,
        'revenue_change_percent': revenue_change,
        'active_campaigns': active_campaigns_count,
        'total_orders_today': total_orders_today,
        'pending_orders': pending_orders_count,
    }
    
    context = {
        # KPI Stats Dictionary
        'stats': stats,
        
        # Individual variables kept for backward compatibility if needed (though template uses stats)
        'today_revenue': today_revenue,
        'revenue_change': revenue_change,
        'last_5_min_sales': last_5_min_sales,
        'active_visitors': active_visitors,
        'avg_cart': avg_cart,
        'pending_orders_count': pending_orders_count,
        
        # Chart Data
        'chart_data': json.dumps(chart_data),
        
        # Performance Data
        'campaign_performance': campaign_performance,
        'recent_orders': recent_orders,
        'top_products': top_products,
        'hourly_comparison': hourly_comparison,
        'product_stats': product_stats,
        'city_performance': city_performance,
    }
    
    return render(request, 'admin_panel/dashboard.html', context)

