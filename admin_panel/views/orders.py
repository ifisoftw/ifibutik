from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Q
from django.core.paginator import Paginator
from orders.models import Order
from campaigns.models import Campaign
from admin_panel.decorators import admin_required
from urllib.parse import urlencode


@admin_required('manage_orders')
def order_list(request):
    """Sipariş listesi"""
    orders = Order.objects.select_related(
        'campaign', 'city_fk', 'district_fk', 'neighborhood_fk'
    ).prefetch_related('items__product')

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
    order = get_object_or_404(Order, pk=pk)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.status = new_status
        order.save()
        
        response = HttpResponse()
        response['HX-Trigger'] = 'orderStatusUpdated'
        return response
    
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

