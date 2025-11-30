from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse
from django.db.models import Count, Q, Max
from django.core.paginator import Paginator
from django.contrib import messages
import json

from campaigns.models import Campaign, CampaignProduct, SizeOption
from products.models import Product
from admin_panel.decorators import admin_required


@admin_required('manage_campaigns')
def campaign_list(request):
    """Kampanya listesi"""
    campaigns = Campaign.objects.annotate(
        product_count=Count('campaignproduct', distinct=True),
        order_count=Count('order', distinct=True)
    )
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        campaigns = campaigns.filter(
            Q(title__icontains=search) |
            Q(description__icontains=search)
        )
    
    # --- Dynamic Counts (Status) ---
    # Calculate counts based on current search, BEFORE status filter
    active_count = campaigns.filter(is_active=True).count()
    inactive_count = campaigns.filter(is_active=False).count()

    # Status filter
    status_filter = request.GET.get('status', '')
    if status_filter == 'active':
        campaigns = campaigns.filter(is_active=True)
    elif status_filter == 'inactive':
        campaigns = campaigns.filter(is_active=False)
    
    # Sorting
    sort = request.GET.get('sort', 'id')
    direction = request.GET.get('dir', 'desc')
    sort_map = {
        'id': 'id',
        'title': 'title',
        'price': 'price',
        'product_count': 'product_count',
        'order_count': 'order_count',
    }
    sort_field = sort_map.get(sort, 'id')
    if direction == 'asc':
        campaigns = campaigns.order_by(sort_field)
    else:
        campaigns = campaigns.order_by(f'-{sort_field}')
    
    # Pagination
    per_page = int(request.GET.get('per_page', 20))
    paginator = Paginator(campaigns, per_page)
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
        'status_counts': {
            'active': active_count,
            'inactive': inactive_count
        }
    }
    
    return render(request, 'admin_panel/campaigns/list.html', context)


@admin_required('manage_campaigns')
def campaign_create_modal(request):
    """Yeni kampanya oluşturma modal'ı (HTMX)"""
    if request.method == 'POST':
        try:
            from django.utils.text import slugify
            
            # Create campaign
            title = request.POST.get('title')
            
            # Auto-generate unique slug from title
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while Campaign.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            
            campaign = Campaign.objects.create(
                title=title,
                slug=slug,
                description=request.POST.get('description', ''),
                price=request.POST.get('price'),
                min_quantity=request.POST.get('min_quantity', 1),
                order=request.POST.get('order', 1),
                shipping_price=request.POST.get('shipping_price', 0),
                shipping_price_discounted=request.POST.get('shipping_price_discounted', 0),
                cod_price=request.POST.get('cod_price', 0),
                cod_price_discounted=request.POST.get('cod_price_discounted', 0),
                is_active=request.POST.get('is_active') == 'on',
            )
            
            # Handle banner upload
            if 'banner_image' in request.FILES:
                campaign.banner_image = request.FILES['banner_image']
                campaign.save()
            
            # Add sizes
            size_ids = request.POST.getlist('sizes')
            if size_ids:
                campaign.available_sizes.set(size_ids)
            
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'campaignListChanged': {},
                'showToast': {'message': 'Kampanya başarıyla oluşturuldu', 'type': 'success'}
            })
            return response
            
        except Exception as e:
            import traceback
            error_detail = traceback.format_exc()
            print(f"=== Campaign Create Error ===\n{error_detail}")
            return HttpResponse(f'<div class="text-red-600 p-4">Hata: {str(e)}</div>', status=400)
    
    # GET request - show form
    products = Product.objects.filter(is_active=True)
    sizes = SizeOption.objects.all()
    
    return render(request, 'admin_panel/campaigns/modals/create.html', {
        'products': products,
        'sizes': sizes,
    })


@admin_required('manage_campaigns')
def campaign_edit_modal(request, pk):
    """Kampanya düzenleme modal'ı (HTMX)"""
    campaign = get_object_or_404(Campaign, pk=pk)
    all_products = Product.objects.filter(is_active=True).exclude(campaignproduct__campaign=campaign)
    campaign_products = campaign.campaignproduct_set.select_related('product').order_by('sort_order')
    sizes = SizeOption.objects.all()
    
    return render(request, 'admin_panel/campaigns/modals/edit.html', {
        'campaign': campaign,
        'all_products': all_products,
        'campaign_products': campaign_products,
        'sizes': sizes,
    })


@admin_required('manage_campaigns')
def campaign_update(request, pk):
    """Kampanya güncelleme (HTMX POST)"""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'POST':
        try:
            # Basic fields
            campaign.title = request.POST.get('title')
            campaign.slug = request.POST.get('slug')
            campaign.description = request.POST.get('description', '')
            campaign.price = request.POST.get('price')
            campaign.min_quantity = request.POST.get('min_quantity')
            campaign.shipping_price = request.POST.get('shipping_price', 0)
            campaign.shipping_price_discounted = request.POST.get('shipping_price_discounted', 0)
            campaign.cod_price = request.POST.get('cod_price', 0)
            campaign.cod_price_discounted = request.POST.get('cod_price_discounted', 0)
            
            # Handle banner upload if provided
            if 'banner_image' in request.FILES:
                campaign.banner_image = request.FILES['banner_image']
            
            campaign.save()
            
            # Update sizes
            size_ids = request.POST.getlist('sizes')
            campaign.available_sizes.set(size_ids)
            
            # Trigger success event
            messages.success(request, 'Kampanya başarıyla güncellendi')
            response = HttpResponse()
            response['HX-Trigger'] = json.dumps({
                'campaignListChanged': {},
                'modalSuccess': {}
            })
            return response
            
        except Exception as e:
            return HttpResponse(
                f'<div class="text-red-600">Hata: {str(e)}</div>',
                status=400
            )
    
    return HttpResponse(status=405)


@admin_required('manage_campaigns')
def campaign_delete(request, pk):
    """Kampanya silme"""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'DELETE' or request.method == 'POST':
        campaign_title = campaign.title
        campaign.delete()
        
        response = HttpResponse()
        response['HX-Trigger'] = json.dumps({
            'campaignDeleted': {},
            'showToast': {'message': 'Kampanya silindi', 'type': 'error'}
        })
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_campaigns')
def campaign_toggle(request, pk):
    """Kampanya aktif/pasif değiştirme"""
    campaign = get_object_or_404(Campaign, pk=pk)
    
    if request.method == 'POST':
        campaign.is_active = not campaign.is_active
        campaign.save()
        
        if campaign.is_active:
            messages.success(request, 'Kampanya aktif yapıldı')
        else:
            messages.warning(request, 'Kampanya pasif yapıldı')
        
        response = HttpResponse()
        response['HX-Trigger'] = 'campaignListChanged'
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_campaigns')
def campaign_bulk_action(request):
    """Toplu kampanya işlemleri"""
    if request.method == 'POST':
        action = request.POST.get('action')
        selected_ids = request.POST.getlist('selected_items')
        
        if not selected_ids:
            return HttpResponse('Kampanya seçilmedi', status=400)
        
        campaigns = Campaign.objects.filter(id__in=selected_ids)
        
        if action == 'activate':
            campaigns.update(is_active=True)
            message = f'{len(selected_ids)} kampanya aktif yapıldı'
        elif action == 'deactivate':
            campaigns.update(is_active=False)
            message = f'{len(selected_ids)} kampanya pasif yapıldı'
        elif action == 'delete':
            count = campaigns.count()
            campaigns.delete()
            message = f'{count} kampanya silindi'
        else:
            return HttpResponse('Geçersiz işlem', status=400)
        
        response = HttpResponse()
        response['HX-Trigger'] = json.dumps({
            'campaignListChanged': {},
            'showToast': {'message': message, 'type': 'success'}
        })
        return response
    
    return HttpResponse(status=405)


@admin_required('manage_campaigns')
def campaign_product_remove(request, pk):
    if request.method != 'POST':
        return HttpResponse(status=405)
        
    campaign_product = get_object_or_404(CampaignProduct, pk=pk)
    campaign = campaign_product.campaign
    campaign_product.delete()
    
    # Get updated list and count
    campaign_products = campaign.campaignproduct_set.select_related('product').order_by('sort_order')
    new_count = campaign_products.count()
    
    # Render updated list
    list_html = render(request, 'admin_panel/campaigns/partials/existing_product_list.html', {
        'campaign_products': campaign_products
    }).content.decode('utf-8')
    
    # Get available products for add list
    available_products = Product.objects.filter(is_active=True).exclude(
        campaignproduct__campaign=campaign
    )[:20]
    
    add_list_html = render(request, 'admin_panel/campaigns/partials/add_product_list.html', {
        'products': available_products,
        'campaign': campaign
    }).content.decode('utf-8')
    
    response = HttpResponse(f"""
        {list_html}
        <span id="campaign-product-count" hx-swap-oob="true" class="px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full text-xs font-semibold">
            {new_count}
        </span>
        <div id="add-product-list" hx-swap-oob="true" class="space-y-2 h-96 overflow-y-auto">
            {add_list_html}
        </div>
    """)
    response['HX-Trigger'] = json.dumps({
        'showToast': {'message': 'Ürün kampanyadan kaldırıldı', 'type': 'success'}
    })
    return response


@admin_required('manage_campaigns')
def campaign_product_reorder(request, pk):
    if request.method != 'POST':
        return HttpResponse(status=405)
        
    campaign_product = get_object_or_404(CampaignProduct, pk=pk)
    sort_order = request.POST.get('sort_order')
    
    if sort_order:
        campaign_product.sort_order = int(sort_order)
        campaign_product.save()
        
    response = HttpResponse()
    response['HX-Trigger'] = json.dumps({
        'showToast': {'message': 'Sıralama güncellendi', 'type': 'success'}
    })
    response = HttpResponse()
    response['HX-Trigger'] = json.dumps({
        'showToast': {'message': 'Sıralama güncellendi', 'type': 'success'}
    })
    return response


@admin_required('manage_campaigns')
def campaign_product_search(request, pk):
    """Kampanya ürün ekleme sekmesi için ürün arama"""
    campaign = get_object_or_404(Campaign, pk=pk)
    products = Product.objects.filter(is_active=True).exclude(
        campaignproduct__campaign=campaign
    )
    
    # Search
    search = request.GET.get('search', '').strip()
    if search:
        products = products.filter(
            Q(name__icontains=search) |
            Q(sku__icontains=search)
        )
    
    # Filter
    filter_type = request.GET.get('filter')
    if filter_type == 'no_campaign':
        products = products.filter(campaignproduct__isnull=True)
    elif filter_type == 'multi_campaign':
        products = products.annotate(
            c_count=Count('campaignproduct')
        ).filter(c_count__gt=0)
        
    # Limit results
    products = products[:20]
    
    return render(request, 'admin_panel/campaigns/partials/add_product_list.html', {
        'products': products,
        'campaign': campaign
    })


@admin_required('manage_campaigns')
def campaign_product_add(request, pk):
    """Kampanyaya ürün ekleme"""
    if request.method != 'POST':
        return HttpResponse(status=405)
        
    campaign = get_object_or_404(Campaign, pk=pk)
    product_id = request.POST.get('product_id')
    product = get_object_or_404(Product, pk=product_id)
    
    # Check if already exists
    if CampaignProduct.objects.filter(campaign=campaign, product=product).exists():
        return HttpResponse(status=400)
        
    # Get max sort order
    max_order = CampaignProduct.objects.filter(campaign=campaign).aggregate(
        Max('sort_order')
    )['sort_order__max'] or 0
    
    CampaignProduct.objects.create(
        campaign=campaign,
        product=product,
        sort_order=max_order + 1
    )
    
    # Get updated list and count
    campaign_products = campaign.campaignproduct_set.select_related('product').order_by('sort_order')
    new_count = campaign_products.count()
    
    # Render updated list
    list_html = render(request, 'admin_panel/campaigns/partials/existing_product_list.html', {
        'campaign_products': campaign_products
    }).content.decode('utf-8')
    
    response = HttpResponse(f"""
        <button disabled 
                x-init="setTimeout(() => $el.closest('.border-gray-200').remove(), 1000)"
                class="p-2 bg-green-500 text-white rounded-lg cursor-default transition-colors">
            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
            </svg>
        </button>
        <span id="campaign-product-count" hx-swap-oob="true" class="px-2 py-0.5 bg-gray-100 text-gray-700 rounded-full text-xs font-semibold">
            {new_count}
        </span>
        <div id="existing-product-list" hx-swap-oob="true" class="space-y-3">
            {list_html}
        </div>
    """)
    response['HX-Trigger'] = json.dumps({
        'showToast': {'message': 'Ürün kampanyaya eklendi', 'type': 'success'}
    })
    return response
