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
from products.models import Product
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

    product_id = request.GET.get('product', '')
    if product_id:
        orders = orders.filter(items__product_id=product_id)

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
    
    # Size filter
    size_filter = request.GET.get('size', '').strip()
    if size_filter:
        orders = orders.filter(items__selected_size__icontains=size_filter).distinct()

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

    # --- Dynamic Filter Counts Calculation ---
    
    # Base queryset with only Search and Date filters (Common for all)
    base_qs = Order.objects.all()
    
    # Apply Search
    if search:
        base_qs = base_qs.filter(
            Q(customer_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(id__icontains=search) |
            Q(tracking_code__icontains=search)
        )
    
    # Apply Date
    if date_from:
        base_qs = base_qs.filter(created_at__date__gte=date_from)
    if date_to:
        base_qs = base_qs.filter(created_at__date__lte=date_to)

    # Helper to apply other filters
    def apply_filters(qs, exclude_filter=None):
        if exclude_filter != 'status' and status:
            qs = qs.filter(status=status)
        if exclude_filter != 'campaign' and campaign_id:
            qs = qs.filter(campaign_id=campaign_id)
        if exclude_filter != 'product' and product_id:
            qs = qs.filter(items__product_id=product_id)
        if exclude_filter != 'size' and size_filter:
            qs = qs.filter(items__selected_size__icontains=size_filter)
        return qs

    # 1. Status Counts (Apply all filters EXCEPT status)
    status_qs = apply_filters(base_qs, exclude_filter='status')
    status_counts_data = status_qs.values('status').annotate(count=Count('id'))
    status_counts = {item['status']: item['count'] for item in status_counts_data}

    # 2. Campaign Counts (Apply all filters EXCEPT campaign)
    campaign_qs = apply_filters(base_qs, exclude_filter='campaign')
    campaign_counts_data = campaign_qs.values('campaign__id').annotate(count=Count('id'))
    campaign_counts = {str(item['campaign__id']): item['count'] for item in campaign_counts_data if item['campaign__id']}

    # 3. Product Counts (Apply all filters EXCEPT product)
    product_qs = apply_filters(base_qs, exclude_filter='product')
    product_counts_data = product_qs.values('items__product__id').annotate(count=Count('id'))
    product_counts = {str(item['items__product__id']): item['count'] for item in product_counts_data if item['items__product__id']}

    # 4. Size Counts (Apply all filters EXCEPT size)
    size_qs = apply_filters(base_qs, exclude_filter='size')
    size_counts_data = size_qs.exclude(items__selected_size__isnull=True).exclude(items__selected_size='').values('items__selected_size').annotate(count=Count('id'))
    size_counts = {item['items__selected_size']: item['count'] for item in size_counts_data}

    # Prepare context data with counts
    
    # Status Choices with Counts
    status_choices_with_counts = []
    for code, label in Order.STATUS_CHOICES:
        count = status_counts.get(code, 0)
        status_choices_with_counts.append((code, label, count))

    # Campaigns with Counts
    campaigns_with_counts = []
    for campaign in Campaign.objects.filter(is_active=True).order_by('title'):
        count = campaign_counts.get(str(campaign.id), 0)
        campaigns_with_counts.append({
            'id': campaign.id,
            'title': campaign.title,
            'count': count
        })

    # Products with Counts
    products_with_counts = []
    for product in Product.objects.filter(is_active=True).order_by('name'):
        count = product_counts.get(str(product.id), 0)
        products_with_counts.append({
            'id': product.id,
            'name': product.name,
            'count': count
        })

    # Sizes with Counts
    # Get all unique sizes first
    all_sizes = OrderItem.objects.filter(selected_size__isnull=False).exclude(selected_size='').values_list('selected_size', flat=True).distinct().order_by('selected_size')
    sizes_with_counts = []
    for size in all_sizes:
        count = size_counts.get(size, 0)
        sizes_with_counts.append({
            'name': size,
            'count': count
        })

    context = {
        'page_obj': page_obj,
        'status': status,
        'search': search,
        'campaign_id': campaign_id,
        'date_from': date_from,
        'date_to': date_to,
        'size_filter': size_filter,
        'per_page': per_page,
        'sort': sort,
        'direction': direction,
        'query_string': base_query,
        'status_choices': status_choices_with_counts, # Updated
        'campaigns': campaigns_with_counts, # Updated
        'products': products_with_counts, # Updated
        'product_id': product_id,
        'available_sizes': sizes_with_counts, # Updated
        'per_page_options': [10, 20, 30, 50],
        'stats': stats,
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
        'campaign', 'city_fk', 'district_fk', 'neighborhood_fk'
    ).prefetch_related('items__product')
    
    return render(request, 'admin_panel/orders/print.html', {
        'orders': orders,
    })

