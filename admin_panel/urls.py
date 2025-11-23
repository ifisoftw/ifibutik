from django.urls import path
from .views import auth as auth_views
from .views import dashboard as dashboard_views
from .views import campaigns as campaign_views
from .views import products as product_views
from .views import orders as order_views
from .views import reports as report_views

urlpatterns = [
    # Authentication
    path('login/', auth_views.admin_login, name='admin_login'),
    path('logout/', auth_views.admin_logout, name='admin_logout'),
    
    # Dashboard
    path('', dashboard_views.dashboard, name='admin_dashboard'),
    
    # Campaigns
    path('campaigns/', campaign_views.campaign_list, name='admin_campaigns'),
    path('campaigns/create/', campaign_views.campaign_create_modal, name='admin_campaign_create'),
    path('campaigns/<int:pk>/edit/', campaign_views.campaign_edit_modal, name='admin_campaign_edit'),
    path('campaigns/<int:pk>/update/', campaign_views.campaign_update, name='admin_campaign_update'),
    path('campaigns/<int:pk>/delete/', campaign_views.campaign_delete, name='admin_campaign_delete'),
    path('campaigns/<int:pk>/toggle/', campaign_views.campaign_toggle, name='admin_campaign_toggle'),
    path('campaigns/bulk-action/', campaign_views.campaign_bulk_action, name='admin_campaign_bulk_action'),
    
    # Products
    path('products/', product_views.product_list, name='admin_products'),
    path('products/create/', product_views.product_create_modal, name='admin_product_create'),
    path('products/<int:pk>/edit/', product_views.product_edit_modal, name='admin_product_edit'),
    path('products/<int:pk>/update/', product_views.product_update, name='admin_product_update'),
    path('products/<int:pk>/delete/', product_views.product_delete, name='admin_product_delete'),
    
    # Orders
    path('orders/', order_views.order_list, name='admin_orders'),
    path('orders/<int:pk>/', order_views.order_detail_modal, name='admin_order_detail'),
    path('orders/<int:pk>/update-status/', order_views.order_update_status, name='admin_order_status'),
    path('orders/<int:pk>/update-cargo/', order_views.order_update_cargo, name='admin_order_cargo'),
    
    # Reports
    path('reports/', report_views.reports, name='admin_reports'),
    path('reports/export/', report_views.export_excel, name='admin_reports_export'),
]

