from django.shortcuts import render
from django.db.models import Count, Sum, Max, F
from django.contrib.auth.decorators import login_required
from ..decorators import admin_required
from orders.models import Order

@login_required
@admin_required('manage_orders') # Using manage_orders permission for now as it's derived from orders
def customer_list(request):
    # Group orders by phone number to simulate customers
    # We use phone as the unique identifier
    customers = Order.objects.values('phone').annotate(
        total_orders=Count('id'),
        total_spent=Sum('total_amount'),
        last_order_date=Max('created_at'),
        customer_name=Max('customer_name'), # Taking one of the names (usually they are same)
        city=Max('city'), # Taking latest city (approx)
        district=Max('district')
    ).order_by('-last_order_date')

    return render(request, 'admin_panel/customers/list.html', {
        'customers': customers
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
