from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q, Sum, Avg, F, Max
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from datetime import timedelta
import json

from products.models import Product, ProductImage
from campaigns.models import Campaign, CampaignProduct
from orders.models import OrderItem
from admin_panel.decorators import admin_required


@admin_required('manage_products')
def product_list(request):
    """Ürün listesi - Kampanyalar sayfasına benzer yapıda"""
    products = Product.objects.prefetch_related(
        'images', 
        'campaignproduct_set__campaign'
    ).annotate(
        campaign_count=Count('campaignproduct', distinct=True),
        total_sales=Count('orderitem', distinct=True),
        revenue=Sum('orderitem__order__total_amount')
    )
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search) |
            Q(description__icontains=search)
        )
    
    # --- Dynamic Filter Counts ---
    
    # Get filter values first
    status_filter = request.GET.get('status', '')
    campaign_filter = request.GET.get('campaign', '')
    
    # Base QuerySet (Search applied, but no other filters yet)
    base_qs = products
    
    # Helper to apply filters
    def apply_filters(qs, exclude_filter=None):
        if exclude_filter != 'status' and status_filter:
            if status_filter == 'active':
                qs = qs.filter(is_active=True)
            elif status_filter == 'inactive':
                qs = qs.filter(is_active=False)
            elif status_filter == 'in_stock':
                qs = qs.filter(stock_qty__gt=0)
            elif status_filter == 'out_of_stock':
                qs = qs.filter(stock_qty=0)
        
        if exclude_filter != 'campaign' and campaign_filter:
            if campaign_filter == 'with_campaign':
                qs = qs.filter(campaign_count__gt=0)
            elif campaign_filter == 'without_campaign':
                qs = qs.filter(campaign_count=0)
            elif campaign_filter == 'multiple':
                qs = qs.filter(campaign_count__gt=1)
        return qs

    # 1. Status Counts (Apply Campaign filter, exclude Status filter)
    status_qs = apply_filters(base_qs, exclude_filter='status')
    status_counts = {
        'active': status_qs.filter(is_active=True).count(),
        'inactive': status_qs.filter(is_active=False).count(),
        'in_stock': status_qs.filter(stock_qty__gt=0).count(),
        'out_of_stock': status_qs.filter(stock_qty=0).count(),
    }

    # 2. Campaign Counts (Apply Status filter, exclude Campaign filter)
    campaign_qs = apply_filters(base_qs, exclude_filter='campaign')
    campaign_counts = {
        'with_campaign': campaign_qs.filter(campaign_count__gt=0).count(),
        'without_campaign': campaign_qs.filter(campaign_count=0).count(),
        'multiple': campaign_qs.filter(campaign_count__gt=1).count(),
    }

    # Apply filters to main queryset for display
    products = apply_filters(base_qs)
    
    # Sorting
    sort = request.GET.get('sort', 'id')
    direction = request.GET.get('dir', 'desc')
    sort_map = {
        'id': 'id',
        'name': 'name',
        'sku': 'sku',
        'stock': 'stock_qty',
        'campaign_count': 'campaign_count',
        'sales': 'total_sales',
    }
    sort_field = sort_map.get(sort, 'id')
    if direction == 'asc':
        products = products.order_by(sort_field)
    else:
        products = products.order_by(f'-{sort_field}')
    
    # Statistics (Global)
    total_products = Product.objects.count()
    active_products = Product.objects.filter(is_active=True).count()
    out_of_stock = Product.objects.filter(stock_qty=0).count()
    low_stock = Product.objects.filter(stock_qty__gt=0, stock_qty__lte=10).count()
    
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
    
    context = {
        'page_obj': page_obj,
        'search': search,
        'status_filter': status_filter,
        'campaign_filter': campaign_filter,
        'sort': sort,
        'direction': direction,
        'query_string': base_query,
        'per_page': per_page,
        'per_page_options': [10, 20, 30, 50],
        'status_counts': status_counts,
        'campaign_counts': campaign_counts,
        'stats': {
            'total': total_products,
            'active': active_products,
            'out_of_stock': out_of_stock,
            'low_stock': low_stock,
        }
    }
    
    return render(request, 'admin_panel/products/list.html', context)


@admin_required('manage_products')
def product_create_modal(request):
    """Yeni ürün oluşturma modal'ı (HTMX)"""
    if request.method == 'POST':
        try:
            # Create product
            product = Product.objects.create(
                name=request.POST.get('name'),
                sku=request.POST.get('sku'),
                description=request.POST.get('description', ''),
                stock_qty=request.POST.get('stock_qty', 0),
                is_active=request.POST.get('is_active') == 'on',
            )
            
            # Handle multiple images
            for img in request.FILES.getlist('images'):
                ProductImage.objects.create(
                    product=product, 
                    image=img,
                    sort_order=0
                )
            
            # Add to campaigns if selected
            campaign_ids = request.POST.getlist('campaigns')
            for campaign_id in campaign_ids:
                campaign = Campaign.objects.get(id=campaign_id)
                # Get max sort order
                max_order = CampaignProduct.objects.filter(
                    campaign=campaign
                ).aggregate(Max('sort_order'))['sort_order__max'] or 0
                
                CampaignProduct.objects.create(
                    campaign=campaign,
                    product=product,
                    sort_order=max_order + 1
                )
            
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
    
    # GET request - show form
    campaigns = Campaign.objects.filter(is_active=True).order_by('title')
    
    return render(request, 'admin_panel/products/modals/create.html', {
        'campaigns': campaigns,
    })


@admin_required('manage_products')
def product_edit_modal(request, pk):
    """Ürün düzenleme modal'ı (HTMX)"""
    product = get_object_or_404(Product, pk=pk)
    all_campaigns = Campaign.objects.filter(is_active=True).order_by('title')
    product_campaigns = product.campaignproduct_set.select_related('campaign')
    product_campaign_ids = [cp.campaign.id for cp in product_campaigns]
    
    return render(request, 'admin_panel/products/modals/edit.html', {
        'product': product,
        'all_campaigns': all_campaigns,
        'product_campaigns': product_campaigns,
        'product_campaign_ids': product_campaign_ids,
    })


@admin_required('manage_products')
def product_update(request, pk):
    """Ürün güncelleme (HTMX POST)"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            # Basic fields
            product.name = request.POST.get('name')
            product.sku = request.POST.get('sku')
            product.description = request.POST.get('description', '')
            product.stock_qty = request.POST.get('stock_qty', 0)
            product.is_active = request.POST.get('is_active') == 'on'
            product.save()
            
            # Handle new images
            for img in request.FILES.getlist('images'):
                ProductImage.objects.create(
                    product=product,
                    image=img,
                    sort_order=0
                )
            
            # Update campaigns
            campaign_ids = request.POST.getlist('campaigns')
            
            # Remove from old campaigns
            product.campaignproduct_set.all().delete()
            
            # Add to new campaigns
            for campaign_id in campaign_ids:
                campaign = Campaign.objects.get(id=campaign_id)
                max_order = CampaignProduct.objects.filter(
                    campaign=campaign
                ).aggregate(Max('sort_order'))['sort_order__max'] or 0
                
                CampaignProduct.objects.create(
                    campaign=campaign,
                    product=product,
                    sort_order=max_order + 1
                )
            
            # Trigger success event
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'productListChanged': {},
                'modalSuccess': {},
                'showToast': {'message': 'Ürün başarıyla güncellendi', 'type': 'success'}
            })
            return response
            
        except Exception as e:
            return HttpResponse(
                f'<div class="text-red-600">Hata: {str(e)}</div>',
                status=400
            )
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def product_delete(request, pk):
    """Ürün silme"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'DELETE' or request.method == 'POST':
        product_name = product.name
        product.delete()
        
        response = HttpResponse()
        response['HX-Trigger'] = json.dumps({
            'productDeleted': {},
            'showToast': {'message': f'{product_name} silindi', 'type': 'error'}
        })
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def product_toggle(request, pk):
    """Ürün aktif/pasif değiştirme"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        product.is_active = not product.is_active
        product.save()
        
        # Re-fetch with annotations for the row
        product = Product.objects.annotate(
            campaign_count=Count('campaignproduct'),
            total_sales=Count('orderitem')
        ).get(pk=pk)
        
        # Render updated row
        from django.template.loader import render_to_string
        row_html = render_to_string('admin_panel/products/partials/product_row.html', {
            'product': product,
            'request': request
        })
        
        if product.is_active:
            message = 'Ürün aktif yapıldı'
            msg_type = 'success'
        else:
            message = 'Ürün pasif yapıldı'
            msg_type = 'warning'
        
        response = HttpResponse(row_html)
        response['HX-Trigger'] = json.dumps({
            'showToast': {'message': message, 'type': msg_type}
        })
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def product_image_delete(request, pk):
    """Ürün görseli silme (HTMX)"""
    if request.method == 'DELETE':
        try:
            image = get_object_or_404(ProductImage, pk=pk)
            image.delete()
            
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'showToast': {'message': 'Görsel başarıyla silindi', 'type': 'success'}
            })
            return response
        except Exception as e:
            return HttpResponse(f'<div class="text-red-600">Hata: {str(e)}</div>', status=400)
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def product_bulk_action(request):
    """Toplu ürün işlemleri"""
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_items')
        
        if not selected_ids:
            return HttpResponse('Ürün seçilmedi', status=400)
        
        products = Product.objects.filter(id__in=selected_ids)
        
        if action == 'activate':
            products.update(is_active=True)
            message = f'{len(selected_ids)} ürün aktif yapıldı'
            msg_type = 'success'
        elif action == 'deactivate':
            products.update(is_active=False)
            message = f'{len(selected_ids)} ürün pasif yapıldı'
            msg_type = 'warning'
        elif action == 'delete':
            count = products.count()
            products.delete()
            message = f'{count} ürün silindi'
            msg_type = 'error'
        elif action == 'add_to_campaign':
            campaign_id = request.POST.get('campaign_id')
            if campaign_id:
                campaign = Campaign.objects.get(id=campaign_id)
                for product in products:
                    if not CampaignProduct.objects.filter(
                        campaign=campaign, 
                        product=product
                    ).exists():
                        max_order = CampaignProduct.objects.filter(
                            campaign=campaign
                        ).aggregate(Max('sort_order'))['sort_order__max'] or 0
                        
                        CampaignProduct.objects.create(
                            campaign=campaign,
                            product=product,
                            sort_order=max_order + 1
                        )
                message = f'{len(selected_ids)} ürün {campaign.title} kampanyasına eklendi'
                msg_type = 'success'
            else:
                return HttpResponse('Kampanya seçilmedi', status=400)
        else:
            return HttpResponse('Geçersiz işlem', status=400)
        
        response = HttpResponse()
        response['HX-Trigger'] = json.dumps({
            'productListChanged': {},
            'showToast': {'message': message, 'type': msg_type}
        })
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def product_image_delete(request, pk, image_id):
    """Ürün görseli silme"""
    product = get_object_or_404(Product, pk=pk)
    image = get_object_or_404(ProductImage, pk=image_id, product=product)
    
    if request.method == 'DELETE' or request.method == 'POST':
        image.delete()
        
        response = HttpResponse()
        response['HX-Trigger'] = json.dumps({
            'imageDeleted': {},
            'showToast': {'message': 'Görsel silindi', 'type': 'success'}
        })
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_products')
def product_stock_update(request, pk):
    """Hızlı stok güncelleme"""
    product = get_object_or_404(Product, pk=pk)
    
    if request.method == 'POST':
        try:
            stock_qty = int(request.POST.get('stock_qty', 0))
            product.stock_qty = stock_qty
            product.save()
            
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'stockUpdated': {},
                'showToast': {'message': 'Stok güncellendi', 'type': 'success'}
            })
            return response
            
        except ValueError:
            return HttpResponse('Geçersiz stok miktarı', status=400)
    
    return HttpResponse(status=405)