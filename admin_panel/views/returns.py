from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..decorators import admin_required
from orders.models import ReturnRequest, Order

@login_required
@admin_required('manage_orders')
def return_list(request):
    """İade talepleri listesi - Modern tasarım ve istatistiklerle"""
    from django.db.models import Q, Count
    from django.core.paginator import Paginator
    
    returns = ReturnRequest.objects.select_related('order').order_by('-created_at')
    
    # Calculate Stats
    stats = {
        'total': ReturnRequest.objects.count(),
        'pending': ReturnRequest.objects.filter(status='pending').count(),
        'approved': ReturnRequest.objects.filter(status='approved').count(),
        'rejected': ReturnRequest.objects.filter(status='rejected').count(),
        'completed': ReturnRequest.objects.filter(status='completed').count(),
    }
    
    # Filters
    status = request.GET.get('status', '')
    if status in dict(ReturnRequest.STATUS_CHOICES):
        returns = returns.filter(status=status)
        
    search = request.GET.get('search', '').strip()
    if search:
        returns = returns.filter(
            Q(order__customer_name__icontains=search) |
            Q(order__phone__icontains=search) |
            Q(id__icontains=search) |
            Q(order__id__icontains=search) |
            Q(iban__icontains=search)
        )
        
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    if date_from:
        returns = returns.filter(created_at__date__gte=date_from)
    if date_to:
        returns = returns.filter(created_at__date__lte=date_to)
        
    # Sorting
    sort = request.GET.get('sort', 'created_at')
    direction = request.GET.get('dir', 'desc')
    sort_map = {
        'id': 'id',
        'order': 'order__id',
        'customer': 'order__customer_name',
        'reason': 'reason',
        'status': 'status',
        'created_at': 'created_at',
    }
    sort_field = sort_map.get(sort, 'created_at')
    if direction == 'asc':
        returns = returns.order_by(sort_field)
    else:
        returns = returns.order_by(f'-{sort_field}')
        
    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(returns, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Build query string for sorting/pagination links
    preserved_query = request.GET.copy()
    for key in ['page', 'sort', 'dir']:
        if key in preserved_query:
            del preserved_query[key]
    base_query = preserved_query.urlencode()
    base_query = f'&{base_query}' if base_query else ''
    
    # Dynamic Status Counts
    # Base queryset for counts (only search and date filters applied)
    base_qs = ReturnRequest.objects.all()
    if search:
        base_qs = base_qs.filter(
            Q(order__customer_name__icontains=search) |
            Q(order__phone__icontains=search) |
            Q(id__icontains=search) |
            Q(order__id__icontains=search) |
            Q(iban__icontains=search)
        )
    if date_from:
        base_qs = base_qs.filter(created_at__date__gte=date_from)
    if date_to:
        base_qs = base_qs.filter(created_at__date__lte=date_to)
        
    status_counts_data = base_qs.values('status').annotate(count=Count('id'))
    status_counts = {item['status']: item['count'] for item in status_counts_data}
    
    status_choices_with_counts = []
    for code, label in ReturnRequest.STATUS_CHOICES:
        count = status_counts.get(code, 0)
        status_choices_with_counts.append((code, label, count))

    return render(request, 'admin_panel/returns/list.html', {
        'page_obj': page_obj,
        'status': status,
        'search': search,
        'date_from': date_from,
        'date_to': date_to,
        'per_page': per_page,
        'sort': sort,
        'direction': direction,
        'query_string': base_query,
        'status_choices': status_choices_with_counts,
        'per_page_options': [20, 50, 100],
        'stats': stats
    })

@login_required
@admin_required('manage_orders')
def return_detail(request, return_id):
    return_request = get_object_or_404(ReturnRequest, id=return_id)
    return render(request, 'admin_panel/returns/detail_modal.html', {
        'return_request': return_request
    })

@login_required
@admin_required('manage_orders')
def return_action(request, return_id):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Geçersiz istek'})
        
    return_request = get_object_or_404(ReturnRequest, id=return_id)
    action = request.POST.get('action')
    note = request.POST.get('note')
    
    if action == 'approve':
        return_request.status = 'approved'
        return_request.admin_note = note
        return_request.save()
        
        # Update Order Status
        order = return_request.order
        order.status = 'return'
        order.save()
        
        messages.success(request, 'İade talebi onaylandı.')
        
    elif action == 'reject':
        return_request.status = 'rejected'
        return_request.admin_note = note
        return_request.save()
        messages.warning(request, 'İade talebi reddedildi.')
        
    elif action == 'complete':
        return_request.status = 'completed'
        return_request.admin_note = note
        return_request.save()
        messages.success(request, 'İade süreci tamamlandı.')
        
    return redirect('admin_returns')

@login_required
@admin_required('manage_orders')
def return_bulk_action(request):
    """Toplu iade işlemleri"""
    import json
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_items')
        
        if not selected_ids:
            return JsonResponse({'error': 'İade talebi seçilmedi'}, status=400)
        
        returns = ReturnRequest.objects.filter(id__in=selected_ids)
        
        if action == 'delete':
            count = returns.count()
            returns.delete()
            response = JsonResponse({'status': 'success'})
            response['HX-Trigger'] = json.dumps({
                'modalSuccess': {}, # Reuse existing event or create new one
                'showToast': {'message': f'{count} iade talebi silindi', 'type': 'success'}
            })
            return response
            
        elif action in ['approved', 'rejected', 'completed']:
            # For approval, we also need to update order status
            if action == 'approved':
                for ret in returns:
                    ret.status = 'approved'
                    ret.save()
                    # Update Order Status
                    order = ret.order
                    order.status = 'return'
                    order.save()
            else:
                returns.update(status=action)
                
            response = JsonResponse({'status': 'success'})
            response['HX-Trigger'] = json.dumps({
                'modalSuccess': {},
                'showToast': {'message': f'{returns.count()} iade talebi güncellendi', 'type': 'success'}
            })
            return response
            
    return JsonResponse({'error': 'Geçersiz istek'}, status=405)
