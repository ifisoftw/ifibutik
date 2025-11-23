from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse
from .models import Campaign
from addresses.models import City, District, Neighborhood

def home_view(request):
    first_campaign = Campaign.objects.filter(is_active=True).first()
    if first_campaign:
        return redirect('campaign_detail', slug=first_campaign.slug)
    return render(request, 'campaigns/no_campaign.html')

def campaign_detail(request, slug):
    campaign = get_object_or_404(Campaign, slug=slug, is_active=True)
    # Fetch other active campaigns for the tab navigation
    other_campaigns = Campaign.objects.filter(is_active=True).exclude(id=campaign.id)
    all_campaigns = Campaign.objects.filter(is_active=True).order_by('id') # Or any specific ordering
    
    # Fetch products via Through Model to respect ordering
    products = campaign.campaignproduct_set.select_related('product').order_by('sort_order')
    
    # Fetch active cities from database
    cities = City.objects.filter(is_active=True).order_by('name')
    
    context = {
        'campaign': campaign,
        'all_campaigns': all_campaigns,
        'products': products,
        'cities': cities,
    }
    return render(request, 'campaigns/detail.html', context)

def get_districts(request):
    city_id = request.GET.get('city')
    districts = []
    
    if city_id:
        districts = District.objects.filter(
            city_id=city_id, 
            is_active=True
        ).order_by('name')
    
    options = '<option value="">İlçe Seçin</option>'
    for district in districts:
        options += f'<option value="{district.id}">{district.name}</option>'
        
    return HttpResponse(options)

def get_neighborhoods(request):
    district_id = request.GET.get('district')
    neighborhoods = []
    
    if district_id:
        neighborhoods = Neighborhood.objects.filter(
            district_id=district_id,
            is_active=True
        ).order_by('name')
    
    options = '<option value="">Mahalle Seçin</option>'
    for neighborhood in neighborhoods:
        options += f'<option value="{neighborhood.id}">{neighborhood.name}</option>'
        
    return HttpResponse(options)
