from functools import wraps
from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.contrib import messages


def admin_required(permission=None):
    """
    Admin kullanıcı gerektiren view'ler için dekoratör
    
    Kullanım:
    @admin_required()
    @admin_required('manage_campaigns')
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Kullanıcı giriş yapmış mı?
            if not request.user.is_authenticated:
                messages.warning(request, 'Bu sayfayı görüntülemek için giriş yapmalısınız.')
                return redirect('admin_login')
            
            # Kullanıcının admin profili var mı?
            if not hasattr(request.user, 'admin_profile'):
                messages.error(request, 'Bu sayfaya erişim yetkiniz bulunmamaktadır.')
                return HttpResponseForbidden('Admin yetkisi gereklidir.')
            
            # Admin profili aktif mi?
            if not request.user.admin_profile.is_active:
                messages.error(request, 'Hesabınız devre dışı bırakılmıştır.')
                return HttpResponseForbidden('Hesap aktif değil.')
            
            # Belirli bir izin gerekiyor mu?
            if permission:
                if not request.user.admin_profile.has_permission(permission):
                    messages.error(request, 'Bu işlem için yetkiniz bulunmamaktadır.')
                    return HttpResponseForbidden(f'{permission} izni gereklidir.')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_permission(user, permission_code):
    """Helper function - kullanıcının izni var mı kontrol et"""
    if not hasattr(user, 'admin_profile'):
        return False
    return user.admin_profile.has_permission(permission_code)

