from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from campaigns import views as campaign_views

urlpatterns = [
    # 1. Django Admin (default)
    path('admin/', admin.site.urls),
    
    # 2. Custom Admin Panel
    path('panel/', include('admin_panel.urls')),
    
    # 3. Frontend
    path('', campaign_views.home_view, name='home'),
    path('', include('campaigns.urls')),
    path('orders/', include('orders.urls')),
]

# 2. Media (Debug mode)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
