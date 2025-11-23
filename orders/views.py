from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from .models import Order, OrderItem
from campaigns.models import Campaign, SizeOption
from products.models import Product
from addresses.models import City, District, Neighborhood
from django.views.decorators.http import require_POST
import json
import random
import string
from django.utils import timezone
from django.utils.timesince import timesince

@require_POST
def create_order(request):
    # Form verilerini al
    campaign_id = request.POST.get('campaign_id')
    campaign = get_object_or_404(Campaign, id=campaign_id)
    
    customer_name = f"{request.POST.get('first_name')} {request.POST.get('last_name')}"
    phone = request.POST.get('phone')
    city_id = request.POST.get('city')
    district_id = request.POST.get('district')
    neighborhood_id = request.POST.get('neighborhood')
    address_detail = request.POST.get('address_detail')
    
    # Adres modellerini çek
    city_obj = get_object_or_404(City, id=city_id) if city_id else None
    district_obj = get_object_or_404(District, id=district_id) if district_id else None
    neighborhood_obj = get_object_or_404(Neighborhood, id=neighborhood_id) if neighborhood_id else None
    
    # Tam adresi oluştur
    neighborhood_name = neighborhood_obj.name if neighborhood_obj else ""
    full_address = f"{neighborhood_name} Mah. {address_detail}" if neighborhood_name else address_detail
    
    # Seçilen ürünleri al (JSON string olarak geliyor veya hidden inputlar)
    # Alpine.js tarafında seçilen ürünleri hidden input olarak göndereceğiz
    # name="selected_products[]" value="product_id"
    # name="selected_sizes[]" value="size_slug" (her ürün için)
    
    selected_product_ids = request.POST.getlist('selected_products[]')
    selected_sizes = request.POST.getlist('selected_sizes[]')
    
    # Basit bir validasyon
    if len(selected_product_ids) < campaign.min_quantity:
        return HttpResponse(f"En az {campaign.min_quantity} adet ürün seçmelisiniz.", status=400)

    # 10 haneli unique tracking number oluştur
    def generate_tracking_number():
        while True:
            tracking = ''.join(random.choices(string.digits, k=10))
            if not Order.objects.filter(tracking_number=tracking).exists():
                return tracking
    
    tracking_number = generate_tracking_number()

    # Siparişi oluştur
    order = Order.objects.create(
        campaign=campaign,
        status='new',
        customer_name=customer_name,
        phone=phone,
        tracking_number=tracking_number,  # Yeni eklenen alan
        # ForeignKey ilişkileri
        city_fk=city_obj,
        district_fk=district_obj,
        neighborhood_fk=neighborhood_obj,
        # Text field'lar (backward compatibility)
        city=city_obj.name if city_obj else "",
        district=district_obj.name if district_obj else "",
        full_address=full_address,
        campaign_price=campaign.price,
        cargo_price=campaign.shipping_price_discounted,  # İndirimli fiyat kullan
        cod_fee=campaign.cod_price_discounted,  # İndirimli fiyat kullan
        total_amount=campaign.price + campaign.shipping_price_discounted + campaign.cod_price_discounted  # Doğru hesaplama
    )
    
    # Sipariş kalemlerini ekle
    for i, product_id in enumerate(selected_product_ids):
        product = Product.objects.get(id=product_id)
        size_slug = selected_sizes[i] if i < len(selected_sizes) else None
        
        # Beden ismini bul (slug'dan)
        size_name = ""
        if size_slug:
            size_obj = SizeOption.objects.filter(slug=size_slug).first()
            if size_obj:
                size_name = size_obj.name

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            selected_size=size_name
        )
        
        # Stok düşme işlemi burada yapılabilir
    
    # Siparişi session'a kaydet (success sayfası için)
    request.session['last_order_id'] = order.id
    request.session['order_completed'] = True
    
    # Başarılı olursa HTMX ile yönlendir
    response = HttpResponse()
    response['HX-Redirect'] = '/orders/success/'
    return response

def order_success(request):
    # Session kontrolü - sadece sipariş sonrası göster
    if not request.session.get('order_completed'):
        return redirect('home')
    
    # Order ID'yi session'dan al
    order_id = request.session.get('last_order_id')
    if not order_id:
        return redirect('home')
    
    # Order'ı getir
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('home')
    
    # Session'ı temizle (tekrar erişimi engelle)
    request.session.pop('order_completed', None)
    request.session.pop('last_order_id', None)
    
    # Order items'ları da getir
    order_items = order.items.select_related('product').all()
    
    context = {
        'order': order,
        'order_items': order_items,
    }
    
    return render(request, 'orders/success.html', context)
    
def social_proof_api(request):
    """
    Returns a random real order for the social proof widget.
    """
    # Get last 20 orders
    recent_orders = Order.objects.filter(
        status__in=['new', 'processing', 'shipped', 'delivered']
    ).select_related('city_fk').prefetch_related('items__product__images').order_by('-created_at')[:20]
    
    if not recent_orders.exists():
        # Fallback if no orders exist yet
        return JsonResponse({}, status=404)
    
    # Pick a random order
    order = random.choice(recent_orders)
    
    # Mask Name (Ayşe Yıl***)
    full_name = order.customer_name.strip()
    parts = full_name.split()
    masked_name = ""
    
    if len(parts) >= 2:
        first_name = parts[0]
        last_name = parts[-1]
        
        if len(last_name) > 2:
            masked_last = last_name[:2] + "***"
        else:
            masked_last = last_name[0] + "***"
            
        masked_name = f"{first_name} {masked_last}"
    else:
        # Single name
        name = parts[0]
        if len(name) > 2:
            masked_name = name[:2] + "***"
        else:
            masked_name = name + "***"
            
    # Location
    location = ""
    if order.city_fk:
        location = order.city_fk.name
    elif order.city:
        location = order.city
    else:
        location = "Türkiye"
        
    # Product
    product_item = order.items.first()
    product_name = "Ürün"
    product_image = "/static/images/placeholder.jpg"
    product_desc = ""
    
    if product_item:
        product = product_item.product
        product_name = product.name
        if product.images.exists():
            product_image = product.images.first().image.url
            
        if product.description:
            desc = product.description
            if len(desc) > 50:
                desc = desc[:47] + "..."
            product_desc = desc
            
    # Time Ago
    now = timezone.now()
    diff = now - order.created_at
    
    if diff.total_seconds() < 300: # Less than 5 minutes
        time_ago = "Şimdi"
    else:
        time_ago = timesince(order.created_at).split(',')[0] # "1 minute" or "2 hours"
        
        # Translate common time strings if needed (basic mapping)
        time_ago = time_ago.replace('minutes', 'dakika').replace('minute', 'dakika')
        time_ago = time_ago.replace('hours', 'saat').replace('hour', 'saat')
        time_ago = time_ago.replace('days', 'gün').replace('day', 'gün')
        time_ago = f"{time_ago} önce"

    data = {
        "name": masked_name,
        "location": location,
        "product_name": product_name,
        "product_image": product_image,
        "product_description": product_desc,
        "time_ago": time_ago
    }
    
    return JsonResponse(data)
