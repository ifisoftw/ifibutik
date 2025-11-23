from django.urls import path
from . import views

urlpatterns = [
    path('ajax/get-districts/', views.get_districts, name='get_districts'),
    path('ajax/get-neighborhoods/', views.get_neighborhoods, name='get_neighborhoods'),
    path('<slug:slug>/', views.campaign_detail, name='campaign_detail'),
]
