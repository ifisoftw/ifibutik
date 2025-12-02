from django.shortcuts import render
from django.db.models import Count, Sum, Max, F
from django.contrib.auth.decorators import login_required
from ..decorators import admin_required
from orders.models import Order

@login_required
@admin_required('manage_orders')
def customer_list(request):
    """Müşteri listesi - Modern tasarım ve istatistiklerle"""
    from django.db.models import Q, Count, Sum, Max
    from django.core.paginator import Paginator
    
    # Base Query - Group by phone to get unique customers
    customers = Order.objects.values('phone').annotate(
        total_orders=Count('id'),
        total_spent=Sum('total_amount'),
        last_order_date=Max('created_at'),
        customer_name=Max('customer_name'),
        city=Max('city'),
        district=Max('district')
    ).order_by('-last_order_date')

    # Calculate Stats (Global)
    total_customers = customers.count()
    total_orders_count = Order.objects.count()
    total_revenue = Order.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    
    stats = {
        'total_customers': total_customers,
        'total_orders': total_orders_count,
        'total_revenue': total_revenue,
        'avg_order_value': total_revenue / total_orders_count if total_orders_count > 0 else 0
    }
    
    # Filters
    search = request.GET.get('search', '').strip()
    if search:
        customers = customers.filter(
            Q(customer_name__icontains=search) |
            Q(phone__icontains=search) |
            Q(city__icontains=search) |
            Q(district__icontains=search)
        )
        
    # Sorting
    sort = request.GET.get('sort', 'last_order_date')
    direction = request.GET.get('dir', 'desc')
    
    # Mapping for sort fields
    sort_map = {
        'customer': 'customer_name',
        'location': 'city',
        'orders': 'total_orders',
        'spent': 'total_spent',
        'last_order': 'last_order_date',
    }
    sort_field = sort_map.get(sort, 'last_order_date')
    
    if direction == 'asc':
        customers = customers.order_by(sort_field)
    else:
        customers = customers.order_by(f'-{sort_field}')
        
    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(customers, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Build query string for sorting/pagination links
    preserved_query = request.GET.copy()
    for key in ['page', 'sort', 'dir']:
        if key in preserved_query:
            del preserved_query[key]
    base_query = preserved_query.urlencode()
    base_query = f'&{base_query}' if base_query else ''

    return render(request, 'admin_panel/customers/list.html', {
        'page_obj': page_obj,
        'search': search,
        'per_page': per_page,
        'sort': sort,
        'direction': direction,
        'query_string': base_query,
        'per_page_options': [20, 50, 100],
        'stats': stats
    })

@login_required
@admin_required('manage_orders')
def customer_detail(request, phone):
    # Get all orders for this customer (phone)
    orders = Order.objects.filter(phone=phone).order_by('-created_at')
    
    # Calculate summary stats
    total_spent = orders.aggregate(Sum('total_amount'))['total_amount__sum'] or 0
    total_orders = orders.count()
    
    # Get the latest customer info
    latest_order = orders.first()
    customer_info = {
        'name': latest_order.customer_name,
        'phone': latest_order.phone,
        'city': latest_order.city,
        'district': latest_order.district,
        'neighborhood': latest_order.neighborhood_fk.name if latest_order.neighborhood_fk else "",
        'address': latest_order.full_address
    }
    
    return render(request, 'admin_panel/customers/detail_modal.html', {
        'orders': orders,
        'customer': customer_info,
        'total_spent': total_spent,
        'total_orders': total_orders
    })

@login_required
@admin_required('export_data')
def customer_export(request):
    import csv
    from django.http import HttpResponse

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="musteriler.csv"'
    
    # Add BOM for Excel compatibility with UTF-8
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response)
    
    # Header
    columns = [
        'Müşteri Adı', 'Telefon', 'İl', 'İlçe', 'Mahalle', 'Tam Adres', 
        'Toplam Sipariş', 'Toplam Harcama', 'Son Sipariş Tarihi'
    ]
    writer.writerow(columns)

    # Filter logic
    queryset = Order.objects.values('phone').annotate(
        total_orders=Count('id'),
        total_spent=Sum('total_amount'),
        last_order_date=Max('created_at'),
        customer_name=Max('customer_name'),
        city=Max('city'),
        district=Max('district'),
        neighborhood=Max('neighborhood_fk__name'),
        full_address=Max('full_address')
    ).order_by('-last_order_date')

    # Check for selected items
    selected_phones = request.GET.get('selected_phones')
    if selected_phones:
        phone_list = selected_phones.split(',')
        queryset = queryset.filter(phone__in=phone_list)

    for customer in queryset:
        writer.writerow([
            customer['customer_name'],
            customer['phone'],
            customer['city'],
            customer['district'],
            customer['neighborhood'] or "",
            customer['full_address'],
            customer['total_orders'],
            f"{customer['total_spent']:.2f}",
            customer['last_order_date'].strftime('%d.%m.%Y %H:%M')
        ])

    return response
