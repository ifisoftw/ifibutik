from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from admin_panel.decorators import admin_required
import csv
import json


@admin_required('view_reports')
def reports(request):
    """Raporlar sayfası"""
    # Tarih aralığı
    end_date = timezone.now().date()
    start_date = end_date - timedelta(days=30)
    
    # Custom date range
    if request.GET.get('start_date'):
        start_date = timezone.datetime.strptime(request.GET.get('start_date'), '%Y-%m-%d').date()
    if request.GET.get('end_date'):
        end_date = timezone.datetime.strptime(request.GET.get('end_date'), '%Y-%m-%d').date()
    
    # Kampanya bazlı rapor
    campaign_qs = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('campaign__title').annotate(
        order_count=Count('id'),
        total_revenue=Sum('total_amount')
    )
    
    campaign_report = campaign_qs.order_by('-order_count')
    campaign_report_revenue = campaign_qs.order_by('-total_revenue')
    
    # Şehir bazlı rapor
    city_qs = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        city_fk__isnull=False
    ).values('city_fk__name').annotate(
        order_count=Count('id'),
        total_revenue=Sum('total_amount')
    )
    
    city_report = city_qs.order_by('-order_count')
    city_report_revenue = city_qs.order_by('-total_revenue')
    
    # ====== En Çok Satan Ürünler ======
    from products.models import Product
    from django.db.models import Q
    
    top_products = Product.objects.annotate(
        sales_count=Count('orderitem', filter=Q(
            orderitem__order__created_at__date__gte=start_date,
            orderitem__order__created_at__date__lte=end_date
        ))
    ).filter(sales_count__gt=0).order_by('-sales_count')
    
    # ====== Grafik Verileri (Günlük Ciro) ======
    chart_dates = []
    chart_revenues = []
    chart_revenues_cumulative = []
    
    current_date = start_date
    cumulative_total = 0
    
    while current_date <= end_date:
        daily_revenue = Order.objects.filter(
            created_at__date=current_date
        ).aggregate(total=Sum('total_amount'))['total'] or 0
        
        cumulative_total += float(daily_revenue)
        
        chart_dates.append(current_date.strftime('%d.%m'))
        chart_revenues.append(float(daily_revenue))
        chart_revenues_cumulative.append(cumulative_total)
        
        current_date += timedelta(days=1)
        
    chart_data = {
        'labels': chart_dates,
        'revenue': chart_revenues,
        'revenue_cumulative': chart_revenues_cumulative
    }
    
    # Karlılık Raporu Hesaplamaları
    # Default Değerler
    default_shipping_cost = 60.0
    default_return_cost = 50.0
    default_undelivered_cost = 70.0

    # Request'ten al veya default kullan
    try:
        shipping_cost = float(request.GET.get('shipping_cost') or default_shipping_cost)
    except (ValueError, TypeError):
        shipping_cost = default_shipping_cost

    try:
        return_cost = float(request.GET.get('return_cost') or default_return_cost)
    except (ValueError, TypeError):
        return_cost = default_return_cost

    try:
        undelivered_cost = float(request.GET.get('undelivered_cost') or default_undelivered_cost)
    except (ValueError, TypeError):
        undelivered_cost = default_undelivered_cost

    # Tarih aralığındaki siparişler
    orders = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    )

    # 1. Temel Sayılar (Leaf Nodes)
    # Çıkış Yapılan Kargo: Yeni ve İşleniyor hariç (Depodan çıkanlar)
    # Not: İptaller şimdilik dahil (Teslim olmayan olarak)
    profitability_orders = orders.exclude(status__in=['new', 'processing'])
    
    count_total = profitability_orders.count()
    count_undelivered = profitability_orders.filter(status='cancelled').count()
    count_return = profitability_orders.filter(status='return').count()
    count_kept = profitability_orders.filter(status='delivered').count() # Teslim edilen ve iade olmayan
    count_shipped = profitability_orders.filter(status='shipped').count() # Yolda olanlar

    # 2. Türetilmiş Sayılar (Parent Nodes)
    count_delivered_initial = count_kept + count_return # Başarılı teslim edilen (İade dahil)

    # 3. Tutarlar (Amounts)
    amount_kept = profitability_orders.filter(status='delivered').aggregate(total=Sum('total_amount'))['total'] or 0
    amount_return = profitability_orders.filter(status='return').aggregate(total=Sum('total_amount'))['total'] or 0
    amount_undelivered = profitability_orders.filter(status='cancelled').aggregate(total=Sum('total_amount'))['total'] or 0
    amount_shipped = profitability_orders.filter(status='shipped').aggregate(total=Sum('total_amount'))['total'] or 0
    
    amount_delivered_initial = amount_kept + amount_return
    # Çıkış Yapılan Kargo Tutarı = Toplam Sipariş Tutarı
    amount_total = profitability_orders.aggregate(total=Sum('total_amount'))['total'] or 0

    # 4. Maliyetler (Costs)
    # Teslim Olmayan: Sabit maliyet
    cost_undelivered = count_undelivered * undelivered_cost
    
    # İade: Gidiş (60) + Dönüş (50)
    cost_return = count_return * (shipping_cost + return_cost)
    
    # Teslim Edilen (Kalan): Sadece Gidiş (60)
    cost_kept = count_kept * shipping_cost
    
    # Yolda Olanlar: Sadece Gidiş (60)
    cost_shipped = count_shipped * shipping_cost
    
    # Toplamlar
    # Teslim Edilen (İlk): Sadece Gidiş Maliyeti (İadelerin dönüş maliyeti buraya dahil edilmez)
    cost_delivered_initial = count_delivered_initial * shipping_cost
    
    # Çıkış Yapılan Kargo Maliyeti (Tablo 1. Sütun): Sadece Gidiş
    cost_outbound_total = count_total * shipping_cost
    
    # İade Dönüş Maliyeti (Sadece dönüş bacağı)
    cost_return_only = count_return * return_cost
    
    # Teslim Olmayan Maliyeti
    cost_undelivered_total = count_undelivered * undelivered_cost
    
    # Genel Toplam Kargo Gideri = Toplam Çıkış + İade Dönüş + Teslim Olmayan
    cost_grand_total = cost_outbound_total + cost_return_only + cost_undelivered_total

    # 5. Oranlar (Rates)
    rate_undelivered = (count_undelivered / count_total * 100) if count_total > 0 else 0
    rate_delivered_initial = (count_delivered_initial / count_total * 100) if count_total > 0 else 0
    # İade Oranı: İade / Toplam Çıkış
    rate_return = (count_return / count_total * 100) if count_total > 0 else 0
    # Teslim Edilen İade Olmayan Oranı
    rate_kept = (count_kept / count_total * 100) if count_total > 0 else 0
    # Yolda Oranı
    rate_shipped = (count_shipped / count_total * 100) if count_total > 0 else 0

    # 6. Özet Kartlar İçin Hesaplamalar
    # Net Kar = (Teslim Edilen İade Olmayan Tutar) - (Genel Toplam Kargo Gideri)
    # Not: Ürün maliyeti dahil değildir.
    net_profit = float(amount_kept) - cost_grand_total
    
    # Beklenen Max Kar: Mevcut Net Kar + Yolda Olanların Cirosu
    # Varsayım: Yolda olanların hepsi teslim edilecek ve iade olmayacak.
    # Not: Yolda olanların kargo maliyeti zaten cost_grand_total (cost_outbound_total) içinde var.
    expected_max_profit = net_profit + float(amount_shipped)

    profitability_data = {
        'shipping_cost': shipping_cost,
        'return_cost': return_cost,
        'undelivered_cost': undelivered_cost,
        
        # Table Data
        'count_total': count_total,
        'count_delivered_initial': count_delivered_initial,
        'count_undelivered': count_undelivered,
        'count_return': count_return,
        'count_kept': count_kept,
        'count_shipped': count_shipped,
        
        'amount_total': amount_total,
        'amount_delivered_initial': amount_delivered_initial,
        'amount_undelivered': amount_undelivered,
        'amount_return': amount_return,
        'amount_kept': amount_kept,
        'amount_shipped': amount_shipped,
        
        'cost_total': cost_outbound_total, # Tablo için (Sadece Gidiş)
        'cost_grand_total': cost_grand_total, # Kart için (Tüm Giderler)
        'cost_delivered_initial': cost_delivered_initial,
        'cost_undelivered': cost_undelivered,
        'cost_return': cost_return,
        'cost_kept': cost_kept,
        'cost_shipped': cost_shipped,
        
        'rate_delivered_initial': rate_delivered_initial,
        'rate_undelivered': rate_undelivered,
        'rate_return': rate_return,
        'rate_kept': rate_kept,
        'rate_shipped': rate_shipped,
        
        # Summary
        'net_profit': net_profit,
        'expected_max_profit': expected_max_profit,
    }

    return render(request, 'admin_panel/reports/index.html', {
        'start_date': start_date,
        'end_date': end_date,
        'campaign_report': campaign_report,
        'campaign_report_revenue': campaign_report_revenue,
        'city_report': city_report,
        'city_report_revenue': city_report_revenue,
        'profitability_data': profitability_data,
        'chart_data': json.dumps(chart_data),
        'top_products': top_products,
    })


@admin_required('export_data')
def export_excel(request):
    """Excel export"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="rapor.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Sipariş No', 'Müşteri', 'Kampanya', 'Tutar', 'Durum', 'Tarih'])
    
    orders = Order.objects.select_related('campaign').order_by('-created_at')[:100]
    for order in orders:
        writer.writerow([
            order.id,
            order.customer_name,
            order.campaign.title if order.campaign else '',
            order.total_amount,
            order.get_status_display(),
            order.created_at.strftime('%d.%m.%Y %H:%M')
        ])
    
    return response

