from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .models import Order, OrderItem
from campaigns.models import Campaign, SizeOption
from products.models import Product
from addresses.models import City, District, Neighborhood
from django.views.decorators.http import require_POST
import json

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

    # Siparişi oluştur
    order = Order.objects.create(
        campaign=campaign,
        status='new',
        customer_name=customer_name,
        phone=phone,
        # ForeignKey ilişkileri
        city_fk=city_obj,
        district_fk=district_obj,
        neighborhood_fk=neighborhood_obj,
        # Text field'lar (backward compatibility)
        city=city_obj.name if city_obj else "",
        district=district_obj.name if district_obj else "",
        full_address=full_address,
        campaign_price=campaign.price,
        cargo_price=campaign.shipping_price, # Şimdilik sabit, mantık eklenebilir
        cod_fee=campaign.cod_price,
        total_amount=campaign.price + campaign.cod_price # Basit hesap
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
    
    # Başarılı olursa HTMX ile yönlendir
    response = HttpResponse()
    response['HX-Redirect'] = '/orders/success/'
    return response

def order_success(request):
    return render(request, 'orders/success.html')
