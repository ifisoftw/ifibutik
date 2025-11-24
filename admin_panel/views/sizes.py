from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from django.contrib import messages
import json

from campaigns.models import SizeOption
from admin_panel.decorators import admin_required


@admin_required('manage_products')
def size_list(request):
    """Beden listesi"""
    sizes = SizeOption.objects.all()
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        sizes = sizes.filter(
            Q(name__icontains=search) |
            Q(slug__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        sizes = sizes.filter(is_active=True)
    elif status_filter == 'inactive':
        sizes = sizes.filter(is_active=False)
    
    # Sorting
    sort = request.GET.get('sort', 'name')
    direction = request.GET.get('dir', 'asc')
    sort_map = {
        'id': 'id',
        'name': 'name',
        'slug': 'slug',
    }
    sort_field = sort_map.get(sort, 'name')
    if direction == 'desc':
        sizes = sizes.order_by(f'-{sort_field}')
    else:
        sizes = sizes.order_by(sort_field)
    
    # Statistics
    total_sizes = SizeOption.objects.count()
    active_sizes = SizeOption.objects.filter(is_active=True).count()
    inactive_sizes = SizeOption.objects.filter(is_active=False).count()
    
    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(sizes, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Preserve query params
    preserved_query = request.GET.copy()
    for key in ['page', 'sort', 'dir']:
        if key in preserved_query:
            del preserved_query[key]
    base_query = preserved_query.urlencode()
    base_query = f'&{base_query}' if base_query else ''
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'sort': sort,
        'direction': direction,
        'query_string': base_query,
        'per_page': per_page,
        'per_page_options': [10, 20, 30, 50],
        'stats': {
            'total': total_sizes,
            'active': active_sizes,
            'inactive': inactive_sizes,
        }
    }
    
    return render(request, 'admin_panel/sizes/list.html', context)


@admin_required('manage_products')
def size_create_modal(request):
    """Yeni beden oluşturma modal'ı (HTMX)"""
    if request.method == 'POST':
        try:
            from django.utils.text import slugify
            
            name = request.POST.get('name')
            slug = request.POST.get('slug')
            
            if not slug:
                slug = slugify(name)
            
            # Check slug uniqueness
            if SizeOption.objects.filter(slug=slug).exists():
                return HttpResponse('<div class="text-red-600 p-4">Bu slug (kod) zaten kullanımda.</div>', status=400)
            
            SizeOption.objects.create(
                name=name,
                slug=slug,
                description=request.POST.get('description', ''),
                is_active=request.POST.get('is_active') == 'on',
            )
            
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'sizeListChanged': {},
                'showToast': {'message': 'Beden başarıyla oluşturuldu', 'type': 'success'}
            })
            return response
            
        except Exception as e:
            return HttpResponse(f'<div class="text-red-600 p-4">Hata: {str(e)}</div>', status=400)
    
    return render(request, 'admin_panel/sizes/modals/create.html')


@admin_required('manage_products')
def size_edit_modal(request, pk):
    """Beden düzenleme modal'ı (HTMX)"""
    size = get_object_or_404(SizeOption, pk=pk)
    
    return render(request, 'admin_panel/sizes/modals/edit.html', {
        'size': size,
    })


@admin_required('manage_products')
def size_update(request, pk):
    """Beden güncelleme (HTMX POST)"""
    size = get_object_or_404(SizeOption, pk=pk)
    
    if request.method == 'POST':
        try:
            from django.utils.text import slugify
            
            name = request.POST.get('name')
            slug = request.POST.get('slug')
            
            if not slug:
                slug = slugify(name)
                
            # Check slug uniqueness (exclude self)
            if SizeOption.objects.filter(slug=slug).exclude(pk=pk).exists():
                return HttpResponse('<div class="text-red-600">Bu slug (kod) zaten kullanımda.</div>', status=400)
            
            size.name = name
            size.slug = slug
            size.description = request.POST.get('description', '')
            size.is_active = request.POST.get('is_active') == 'on'
            size.save()
            
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'sizeListChanged': {},
                'modalSuccess': {},
                'showToast': {'message': 'Beden başarıyla güncellendi', 'type': 'success'}
            })
            return response
            
        except Exception as e:
            return HttpResponse(
                f'<div class="text-red-600">Hata: {str(e)}</div>',
                status=400
            )
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def size_delete(request, pk):
    """Beden silme"""
    size = get_object_or_404(SizeOption, pk=pk)
    
    if request.method == 'DELETE' or request.method == 'POST':
        size_name = size.name
        size.delete()
        
        response = HttpResponse()
        response['HX-Trigger'] = json.dumps({
            'sizeDeleted': {},
            'showToast': {'message': f'{size_name} silindi', 'type': 'error'}
        })
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def size_toggle(request, pk):
    """Beden aktif/pasif değiştirme"""
    size = get_object_or_404(SizeOption, pk=pk)
    
    if request.method == 'POST':
        size.is_active = not size.is_active
        size.save()
        
        # Render updated row
        from django.template.loader import render_to_string
        row_html = render_to_string('admin_panel/sizes/partials/size_row.html', {
            'size': size,
            'request': request
        })
        
        if size.is_active:
            message = 'Beden aktif yapıldı'
            msg_type = 'success'
        else:
            message = 'Beden pasif yapıldı'
            msg_type = 'warning'
        
        response = HttpResponse(row_html)
        response['HX-Trigger'] = json.dumps({
            'showToast': {'message': message, 'type': msg_type}
        })
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def size_bulk_action(request):
    """Toplu beden işlemleri"""
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_items')
        
        if not selected_ids:
            return HttpResponse('Beden seçilmedi', status=400)
        
        sizes = SizeOption.objects.filter(id__in=selected_ids)
        
        if action == 'activate':
            sizes.update(is_active=True)
            message = f'{len(selected_ids)} beden aktif yapıldı'
            msg_type = 'success'
        elif action == 'deactivate':
            sizes.update(is_active=False)
            message = f'{len(selected_ids)} beden pasif yapıldı'
            msg_type = 'warning'
        elif action == 'delete':
            count = sizes.count()
            sizes.delete()
            message = f'{count} beden silindi'
            msg_type = 'error'
        else:
            return HttpResponse('Geçersiz işlem', status=400)
        
        response = HttpResponse()
        response['HX-Trigger'] = json.dumps({
            'sizeListChanged': {},
            'showToast': {'message': message, 'type': msg_type}
        })
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def size_quick_create(request):
    """Kampanya düzenleme modalı içinden hızlı beden ekleme"""
    if request.method == 'POST':
        try:
            from django.utils.text import slugify
            from campaigns.models import Campaign
            
            name = request.POST.get('name')
            description = request.POST.get('description', '')
            campaign_id = request.POST.get('campaign_id')
            
            if not name:
                return HttpResponse('Beden ismi gerekli', status=400)
                
            slug = slugify(name)
            
            # Create or get size
            size, created = SizeOption.objects.get_or_create(
                slug=slug,
                defaults={'name': name, 'description': description, 'is_active': True}
            )
            
            # If campaign_id is provided, we need to pass the campaign object to the template
            # so the checkbox logic (checked/unchecked) works correctly.
            # However, since this is a NEW size, it won't be in campaign.available_sizes yet
            # UNLESS we add it. But the form hasn't been submitted yet.
            # The user just wants to ADD the size option to the list so they can check it.
            # OR, they might expect it to be auto-checked.
            
            campaign = None
            if campaign_id:
                campaign = get_object_or_404(Campaign, pk=campaign_id)
            
            # Get all sizes for the list
            sizes = SizeOption.objects.filter(is_active=True).order_by('name')
            
            context = {
                'sizes': sizes,
                'campaign': campaign,
                # We can pass the newly created size ID to auto-check it in the template if we modify the partial
                # But for now, let's just return the list.
                # Actually, if we want it auto-selected, we might need to handle that in the partial or JS.
                # Let's rely on the user checking it, or we can pass a 'new_size_id' to context.
            }
            
            return render(request, 'admin_panel/campaigns/partials/size_checkboxes.html', context)
            
        except Exception as e:
            return HttpResponse(f'<div class="text-red-600">Hata: {str(e)}</div>', status=400)
            
    return HttpResponse(status=405)
