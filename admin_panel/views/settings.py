from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import SiteSettings
from ..decorators import admin_required

@login_required
@admin_required()
def settings_view(request):
    settings = SiteSettings.load()
    
    if request.method == 'POST':
        # Store Info
        settings.store_name = request.POST.get('store_name', settings.store_name)
        settings.store_slogan = request.POST.get('store_slogan', settings.store_slogan)
        settings.store_description = request.POST.get('store_description', settings.store_description)
        
        if 'store_logo' in request.FILES:
            settings.store_logo = request.FILES['store_logo']
            
        # Contact
        settings.whatsapp_number = request.POST.get('whatsapp_number', settings.whatsapp_number)
        settings.instagram_url = request.POST.get('instagram_url', settings.instagram_url)
        settings.facebook_url = request.POST.get('facebook_url', settings.facebook_url)
        
        # Integrations
        settings.gtm_id = request.POST.get('gtm_id', settings.gtm_id)
        settings.ga4_id = request.POST.get('ga4_id', settings.ga4_id)
        settings.pixel_id = request.POST.get('pixel_id', settings.pixel_id)
        settings.hotjar_id = request.POST.get('hotjar_id', settings.hotjar_id)
        settings.contentsquare_id = request.POST.get('contentsquare_id', settings.contentsquare_id)
        settings.onesignal_app_id = request.POST.get('onesignal_app_id', settings.onesignal_app_id)
        settings.facebook_domain_verification = request.POST.get('facebook_domain_verification', settings.facebook_domain_verification)
        
        settings.save()
        messages.success(request, 'Ayarlar başarıyla güncellendi.')
        return redirect('admin_settings')

    return render(request, 'admin_panel/settings.html', {
        'settings': settings
    })
