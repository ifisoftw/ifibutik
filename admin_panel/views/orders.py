from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Q, Count, Sum
from django.core.paginator import Paginator
from django.utils import timezone
from datetime import timedelta
import json
import csv
from orders.models import Order, OrderItem
from campaigns.models import Campaign
from admin_panel.decorators import admin_required
from urllib.parse import urlencode


@admin_required('manage_orders')
def order_list(request):
    """Sipariş listesi - Modern tasarım ve istatistiklerle"""
    orders = Order.objects.select_related(
        'campaign', 'city_fk', 'district_fk', 'neighborhood_fk'
    ).prefetch_related('items__product')

    # Calculate statistics
    today = timezone.now().date()
    month_start = today.replace(day=1)
    
    stats = {
        'total': Order.objects.count(),
        'pending': Order.objects.filter(status='new').count(),
        'processing': Order.objects.filter(status='processing').count(),
        'shipped': Order.objects.filter(status='shipped').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
        'today': Order.objects.filter(created_at__date=today).count(),
        'today_revenue': Order.objects.filter(
            created_at__date=today
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
        'month_revenue': Order.objects.filter(
            created_at__date__gte=month_start
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0,
    }

    # Filters
    status = request.GET.get('status', '')
    if status in dict(Order.STATUS_CHOICES):
        orders = orders.filter(status=status)

    campaign_id = request.GET.get('campaign', '')
    if campaign_id:
        orders = orders.filter(campaign_id=campaign_id)

    search = request.GET.get('search', '').strip()
    if search:
        orders = orders.filter(
            Q(customer_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(id__icontains=search) |
            Q(tracking_code__icontains=search)
        )

    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        orders = orders.filter(created_at__date__gte=date_from)
    if date_to:
        orders = orders.filter(created_at__date__lte=date_to)

    # Sorting
    sort = request.GET.get('sort', 'created_at')
    direction = request.GET.get('dir', 'desc')
    sort_map = {
        'id': 'id',
        'customer': 'customer_name',
        'amount': 'total_amount',
        'created_at': 'created_at',
        'status': 'status',
    }
    sort_field = sort_map.get(sort, 'created_at')
    if direction == 'asc':
        orders = orders.order_by(sort_field)
    else:
        orders = orders.order_by(f'-{sort_field}')

    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(orders, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Build query string for sorting/pagination links
    preserved_query = request.GET.copy()
    for key in ['page', 'sort', 'dir']:
        if key in preserved_query:
            del preserved_query[key]
    base_query = preserved_query.urlencode()
    base_query = f'&{base_query}' if base_query else ''

    context = {
        'page_obj': page_obj,
        'status': status,
        'search': search,
        'campaign_id': campaign_id,
        'date_from': date_from,
        'date_to': date_to,
        'per_page': per_page,
        'sort': sort,
        'direction': direction,
        'query_string': base_query,
        'status_choices': Order.STATUS_CHOICES,
        'campaigns': Campaign.objects.filter(is_active=True).order_by('title'),
        'per_page_options': [10, 20, 30, 50],
        'stats': stats,  # İstatistikler eklendi
    }
    return render(request, 'admin_panel/orders/list.html', context)


@admin_required('manage_orders')
def order_detail_modal(request, pk):
    """Sipariş detay modal - 3 tab"""
    order = get_object_or_404(
        Order.objects.select_related(
            'campaign', 'city_fk', 'district_fk', 'neighborhood_fk'
        ).prefetch_related('items__product__images'),
        pk=pk
    )
    
    return render(request, 'admin_panel/orders/modals/detail.html', {
        'order': order,
    })


@admin_required('manage_orders')
def order_update_status(request, pk):
    """Sipariş durumu güncelleme"""
    order = get_object_or_404(
        Order.objects.select_related(
            'campaign', 'city_fk', 'district_fk', 'neighborhood_fk'
        ).prefetch_related('items__product'),
        pk=pk
    )
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        
        # Return the updated row
        return render(request, 'admin_panel/orders/partials/order_row.html', {
            'order': order,
        })
    
    return HttpResponse(status=405)


@admin_required('manage_orders')
def order_update_cargo(request, pk):
    """Kargo bilgileri güncelleme"""
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        order.cargo_firm = request.POST.get('cargo_firm', '')
        order.tracking_code = request.POST.get('tracking_code', '')
        order.cargo_barcode = request.POST.get('cargo_barcode', '')
        order.save()
        
        response = HttpResponse()
        response['HX-Trigger'] = 'cargoUpdated'
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_orders')
def order_bulk_action(request):
    """Toplu sipariş işlemleri"""
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_items')
        
        if not selected_ids:
            return JsonResponse({'error': 'Sipariş seçilmedi'}, status=400)
        
        orders = Order.objects.filter(id__in=selected_ids)
        
        if action == 'delete':
            count = orders.count()
            orders.delete()
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'orderListChanged': {},
                'showToast': {'message': f'{count} sipariş silindi', 'type': 'success'}
            })
            return response
            
        elif action in ['new', 'processing', 'shipped', 'delivered', 'cancelled', 'return']:
            orders.update(status=action)
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'orderListChanged': {},
                'showToast': {'message': f'{orders.count()} sipariş durumu güncellendi', 'type': 'success'}
            })
            return response
            
        elif action == 'export':
            # CSV Export
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="siparisler_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'
            response.write('\ufeff')  # BOM for Excel UTF-8
            
            writer = csv.writer(response)
            writer.writerow(['Sipariş No', 'Müşteri', 'Telefon', 'Kampanya', 'Tutar', 'Durum', 'Tarih', 'Adres'])
            
            for order in orders:
                writer.writerow([
                    f'#{order.id}',
                    order.customer_name,
                    order.phone,
                    order.campaign.title if order.campaign else '-',
                    f'₺{order.total_amount}',
                    order.get_status_display(),
                    order.created_at.strftime('%d.%m.%Y %H:%M'),
                    f'{order.full_address}, {order.district}, {order.city}'
                ])
            
            return response
            
        elif action == 'print':
            # Toplu yazdırma için sipariş listesini session'a kaydet
            request.session['print_orders'] = selected_ids
            return JsonResponse({'redirect': '/panel/orders/print/'})
    
    return HttpResponse(status=405)


@admin_required('manage_orders')
def order_print_view(request):
    """Toplu yazdırma sayfası"""
    if request.method == 'POST':
        order_ids = request.POST.getlist('selected_items')
    else:
        order_ids = request.session.get('print_orders', [])
    
    if not order_ids:
        return HttpResponse('Yazdırılacak sipariş bulunamadı', status=404)
    
    orders = Order.objects.filter(id__in=order_ids).select_related(
        'campaign'
    ).prefetch_related('items__product')
    
    return render(request, 'admin_panel/orders/print.html', {
        'orders': orders,
    })

