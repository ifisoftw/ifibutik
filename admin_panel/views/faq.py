from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from ..models import FAQ
from ..decorators import admin_required

@login_required
@admin_required('manage_settings')
@require_http_methods(["POST"])
def faq_create(request):
    question = request.POST.get('question')
    answer = request.POST.get('answer')
    order = request.POST.get('order', 0)
    is_active = request.POST.get('is_active') == 'on'

    if question and answer:
        FAQ.objects.create(
            question=question,
            answer=answer,
            order=order,
            is_active=is_active
        )
        messages.success(request, 'SSS başarıyla eklendi.')
    else:
        messages.error(request, 'Soru ve cevap alanları zorunludur.')
    
    return redirect('admin_settings')

@login_required
@admin_required('manage_settings')
@require_http_methods(["POST"])
def faq_update(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    
    question = request.POST.get('question')
    answer = request.POST.get('answer')
    order = request.POST.get('order', 0)
    is_active = request.POST.get('is_active') == 'on'

    if question and answer:
        faq.question = question
        faq.answer = answer
        faq.order = order
        faq.is_active = is_active
        faq.save()
        messages.success(request, 'SSS başarıyla güncellendi.')
    else:
        messages.error(request, 'Soru ve cevap alanları zorunludur.')
    
    return redirect('admin_settings')

@login_required
@admin_required('manage_settings')
@require_http_methods(["POST"])
def faq_delete(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    faq.delete()
    messages.success(request, 'SSS başarıyla silindi.')
    return redirect('admin_settings')

@login_required
@admin_required('manage_settings')
@require_http_methods(["POST"])
@login_required
@admin_required('manage_settings')
@require_http_methods(["POST"])
def faq_toggle(request, pk):
    faq = get_object_or_404(FAQ, pk=pk)
    faq.is_active = not faq.is_active
    faq.save()
    
    if request.headers.get('HX-Request'):
        # Return the updated button HTML
        from django.template.loader import render_to_string
        return render(request, 'admin_panel/partials/faq_toggle_button.html', {'faq': faq})
    
    status_text = 'aktif' if faq.is_active else 'pasif'
    messages.success(request, f'SSS durumu {status_text} olarak güncellendi.')
    return redirect('admin_settings')
