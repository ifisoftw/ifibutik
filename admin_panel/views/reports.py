from django.shortcuts import render
from django.http import HttpResponse
from django.db.models import Sum, Count
from django.utils import timezone
from datetime import timedelta
from orders.models import Order
from admin_panel.decorators import admin_required
import csv


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
    campaign_report = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date
    ).values('campaign__title').annotate(
        order_count=Count('id'),
        total_revenue=Sum('total_amount')
    ).order_by('-total_revenue')
    
    # Şehir bazlı rapor
    city_report = Order.objects.filter(
        created_at__date__gte=start_date,
        created_at__date__lte=end_date,
        city_fk__isnull=False
    ).values('city_fk__name').annotate(
        order_count=Count('id'),
        total_revenue=Sum('total_amount')
    ).order_by('-total_revenue')
    
    return render(request, 'admin_panel/reports/index.html', {
        'start_date': start_date,
        'end_date': end_date,
        'campaign_report': campaign_report,
        'city_report': city_report,
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

