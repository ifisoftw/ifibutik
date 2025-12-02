from django.shortcuts import render, redirect
import os
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from ..models import SiteSettings, FAQ
from ..decorators import admin_required

@login_required
@admin_required('manage_settings')
def settings_view(request):
    settings = SiteSettings.load()
    faqs = FAQ.objects.all().order_by('order', '-created_at')
    
    if request.method == 'POST':
        # Store Info
        settings.store_name = request.POST.get('store_name', settings.store_name)
        settings.store_slogan = request.POST.get('store_slogan', settings.store_slogan)
        settings.store_description = request.POST.get('store_description', settings.store_description)
        
        if 'store_logo' in request.FILES:
            logo_file = request.FILES['store_logo']
            
            # GÜVENLİK: Dosya Yükleme Kontrolü
            # 1. Uzantı Kontrolü
            valid_extensions = ['.jpg', '.jpeg', '.png']
            ext = os.path.splitext(logo_file.name)[1].lower()
            if ext not in valid_extensions:
                messages.error(request, 'Güvenlik Hatası: Sadece JPG ve PNG dosyaları yüklenebilir.')
                return redirect('admin_settings')
            
            # 2. Boyut Kontrolü (Max 2MB)
            if logo_file.size > 2 * 1024 * 1024:
                messages.error(request, 'Hata: Dosya boyutu 2MB\'dan büyük olamaz.')
                return redirect('admin_settings')

            # 3. İçerik Kontrolü (Pillow ile)
            try:
                from PIL import Image
                img = Image.open(logo_file)
                img.verify()  # Verify that it is, in fact, an image
                logo_file.seek(0)  # Reset file pointer after verify
            except Exception:
                messages.error(request, 'Hata: Geçersiz resim dosyası.')
                return redirect('admin_settings')

            settings.store_logo = logo_file
            
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
        
        # Interface Messages
        settings.info_note_title = request.POST.get('info_note_title', settings.info_note_title)
        settings.info_note_content = request.POST.get('info_note_content', settings.info_note_content)
        
        # Security
        try:
            count = int(request.POST.get('rate_limit_count', settings.rate_limit_count))
            period = int(request.POST.get('rate_limit_period', settings.rate_limit_period))
            
            if count > 0 and period > 0:
                settings.rate_limit_count = count
                settings.rate_limit_period = period
            else:
                messages.error(request, 'Hata: Rate limit değerleri pozitif olmalıdır.')
        except (ValueError, TypeError):
            messages.error(request, 'Hata: Geçersiz sayı formatı.')
        
        settings.save()
        messages.success(request, 'Ayarlar başarıyla güncellendi.')
        return redirect('admin_settings')

    return render(request, 'admin_panel/settings.html', {
        'settings': settings,
        'faqs': faqs
    })
