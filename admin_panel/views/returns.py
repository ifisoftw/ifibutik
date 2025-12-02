from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from ..decorators import admin_required
from orders.models import ReturnRequest, Order

@login_required
@admin_required('manage_orders')
def return_list(request):
    status_filter = request.GET.get('status')
    
    returns = ReturnRequest.objects.all().select_related('order').order_by('-created_at')
    
    # Calculate Stats
    stats = {
        'total': ReturnRequest.objects.count(),
        'pending': ReturnRequest.objects.filter(status='pending').count(),
        'approved': ReturnRequest.objects.filter(status='approved').count(),
        'rejected': ReturnRequest.objects.filter(status='rejected').count(),
    }
    
    if status_filter:
        returns = returns.filter(status=status_filter)
        
    return render(request, 'admin_panel/returns/list.html', {
        'returns': returns,
        'current_status': status_filter,
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
