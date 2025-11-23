from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def admin_login(request):
    """Admin panel login view"""
    # Eğer zaten giriş yapmışsa dashboard'a yönlendir
    if request.user.is_authenticated and hasattr(request.user, 'admin_profile'):
        return redirect('admin_dashboard')
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Kullanıcının admin profili var mı kontrol et
            if hasattr(user, 'admin_profile') and user.admin_profile.is_active:
                login(request, user)
                messages.success(request, f'Hoş geldiniz, {user.get_full_name() or user.username}!')
                
                # Redirect to next or dashboard
                next_url = request.GET.get('next', 'admin_dashboard')
                return redirect(next_url)
            else:
                messages.error(request, 'Bu hesabın admin panel erişimi bulunmamaktadır.')
        else:
            messages.error(request, 'Kullanıcı adı veya şifre hatalı.')
    
    return render(request, 'admin_panel/auth/login.html')


def admin_logout(request):
    """Admin panel logout view"""
    logout(request)
    messages.info(request, 'Başarıyla çıkış yaptınız.')
    return redirect('admin_login')

