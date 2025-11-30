from .middleware import get_active_user_count
from admin_panel.models import SiteSettings

def active_user_count(request):
    return {
        'active_user_count': get_active_user_count(),
        'site_settings': SiteSettings.load()
    }
