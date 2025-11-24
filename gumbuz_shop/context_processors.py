from .middleware import get_active_user_count

def active_user_count(request):
    return {
        'active_user_count': get_active_user_count()
    }
