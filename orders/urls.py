from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('success/', views.order_success, name='order_success'),
    path('api/social-proof/', views.social_proof_api, name='social_proof_api'),
    
    # Return Module
    path('iade-talepi/', views.return_lookup, name='return_lookup'),
    path('iade-talepi/olustur/', views.return_create, name='return_create'),
    path('iade-talepi/basarili/', views.return_success, name='return_success'),
]

