from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.db.models import Count, Q
from django.core.paginator import Paginator
from products.models import Product
from admin_panel.decorators import admin_required
import json


@admin_required('manage_products')
def product_list(request):
    """Ürün listesi"""
    products = Product.objects.prefetch_related('images', 'campaignproduct_set__campaign').annotate(
        campaign_count=Count('campaignproduct')
    )
    
    # Filters
    filter_type = request.GET.get('filter', 'all')
    if filter_type == 'with_campaign':
        products = products.filter(campaign_count__gt=0)
    elif filter_type == 'without_campaign':
        products = products.filter(campaign_count=0)
    elif filter_type == 'multiple_campaigns':
        products = products.filter(campaign_count__gt=1)
    elif filter_type == 'active':
        products = products.filter(is_active=True)
    elif filter_type == 'inactive':
        products = products.filter(is_active=False)
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        products = products.filter(
            Q(name__icontains=search) | 
            Q(sku__icontains=search) |
            Q(description__icontains=search)
        )
    
    # Sorting
    sort = request.GET.get('sort', 'id')
    direction = request.GET.get('dir', 'desc')
    sort_map = {
        'id': 'id',
        'name': 'name',
        'sku': 'sku',
        'campaign_count': 'campaign_count',
    }
    sort_field = sort_map.get(sort, 'id')
    if direction == 'asc':
        products = products.order_by(sort_field)
    else:
        products = products.order_by(f'-{sort_field}')
    
    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(products, per_page)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Preserve query params
    preserved_query = request.GET.copy()
    for key in ['page', 'sort', 'dir']:
        if key in preserved_query:
            del preserved_query[key]
    base_query = preserved_query.urlencode()
    base_query = f'&{base_query}' if base_query else ''
    
    filter_options = [
        ('all', 'Tümü'),
        ('active', 'Aktif'),
        ('inactive', 'Pasif'),
        ('with_campaign', 'Kampanyalı'),
        ('without_campaign', 'Kampanyasız'),
        ('multiple_campaigns', 'Çoklu Kampanya'),
    ]
    
    return render(request, 'admin_panel/products/list.html', {
        'page_obj': page_obj,
        'filter_type': filter_type,
        'filter_options': filter_options,
        'search': search,
        'sort': sort,
        'direction': direction,
        'query_string': base_query,
        'per_page': per_page,
        'per_page_options': [10, 20, 30, 50],
    })


@admin_required('manage_products')
def product_create_modal(request):
    """Yeni ürün oluşturma modal"""
    if request.method == 'POST':
        try:
            from products.models import ProductImage
            
            # Create product
            product = Product.objects.create(
                name=request.POST.get('name'),
                sku=request.POST.get('sku'),
                description=request.POST.get('description', ''),
                is_active=request.POST.get('is_active') == 'on',
            )
            
            # Handle multiple images
            for img in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=img)
            
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'productListChanged': {},
                'showToast': {'message': 'Ürün başarıyla oluşturuldu', 'type': 'success'}
            })
            return response
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"=== Product Create Error ===\n{error_detail}")
            return HttpResponse(f'<div class="text-red-600 p-4">Hata: {str(e)}</div>', status=400)
    
    return render(request, 'admin_panel/products/modals/create.html')


@admin_required('manage_products')
def product_edit_modal(request, pk):
    """Ürün düzenleme modal"""
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'admin_panel/products/modals/edit.html', {
        'product': product,
    })


@admin_required('manage_products')
def product_update(request, pk):
    """Ürün güncelleme"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            from products.models import ProductImage
            
            product.name = request.POST.get('name')
            product.sku = request.POST.get('sku')
            product.description = request.POST.get('description', '')
            product.is_active = request.POST.get('is_active') == 'on'
            product.save()
            
            # Handle new images
            for img in request.FILES.getlist('images'):
                ProductImage.objects.create(product=product, image=img)
            
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'productListChanged': {},
                'showToast': {'message': 'Ürün başarıyla güncellendi', 'type': 'success'}
            })
            return response
            
        except Exception as e:
            return HttpResponse(f'<div class="text-red-600 p-4">Hata: {str(e)}</div>', status=400)
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def product_delete(request, pk):
    """Ürün silme"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'DELETE' or request.method == 'POST':
        product.delete()
        response = HttpResponse()
        response['HX-Trigger'] = 'productDeleted'
        return response
    
    return HttpResponse(status=405)

