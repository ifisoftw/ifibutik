from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from campaigns import views as campaign_views
from orders import views as order_views

urlpatterns = [
    # 1. Django Admin (default)
    path('admin/', admin.site.urls),
    
    # 2. Custom Admin Panel
    path('panel/', include('admin_panel.urls')),
    
    # 3. Frontend
    # Return Module (Must be before campaigns to avoid slug conflict)
    path('iade-talepi/', order_views.return_lookup, name='return_lookup'),
    path('iade-talepi/olustur/', order_views.return_create, name='return_create'),
    path('iade-talepi/basarili/', order_views.return_success, name='return_success'),
    
    # Orders (Must be before campaigns)
    path('orders/', include('orders.urls')),
    
    # Campaigns (Catch-all slug)
    path('', campaign_views.home_view, name='home'),
    path('', include('campaigns.urls')),
]

# 2. Media (Debug mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
