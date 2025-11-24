from django.urls import path
from .views import auth as auth_views
from .views import dashboard as dashboard_views
from .views import campaigns as campaign_views
from .views import products as product_views
from .views import orders as order_views
from .views import reports as report_views
from .views import sizes as size_views

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
    path('campaigns/products/<int:pk>/remove/', campaign_views.campaign_product_remove, name='admin_campaign_product_remove'),
    path('campaigns/products/<int:pk>/reorder/', campaign_views.campaign_product_reorder, name='admin_campaign_product_reorder'),
    path('campaigns/<int:pk>/products/search/', campaign_views.campaign_product_search, name='admin_campaign_product_search'),
    path('campaigns/<int:pk>/products/add/', campaign_views.campaign_product_add, name='admin_campaign_product_add'),
    
    # Products
    path('products/', product_views.product_list, name='admin_products'),
    path('products/create/', product_views.product_create_modal, name='admin_product_create'),
    path('products/<int:pk>/edit/', product_views.product_edit_modal, name='admin_product_edit'),
    path('products/<int:pk>/update/', product_views.product_update, name='admin_product_update'),
    path('products/<int:pk>/delete/', product_views.product_delete, name='admin_product_delete'),
    path('products/<int:pk>/toggle/', product_views.product_toggle, name='admin_product_toggle'),
    path('products/bulk-action/', product_views.product_bulk_action, name='admin_product_bulk_action'),
    path('products/image/<int:pk>/delete/', product_views.product_image_delete, name='admin_product_image_delete'),
    path('products/<int:pk>/images/<int:image_id>/delete/', product_views.product_image_delete, name='admin_product_image_delete'),
    path('products/<int:pk>/stock/', product_views.product_stock_update, name='admin_product_stock_update'),
    
    # Orders
    path('orders/', order_views.order_list, name='admin_orders'),
    path('orders/<int:pk>/', order_views.order_detail_modal, name='admin_order_detail'),
    path('orders/<int:pk>/update-status/', order_views.order_update_status, name='admin_order_status'),
    path('orders/<int:pk>/update-cargo/', order_views.order_update_cargo, name='admin_order_cargo'),
    path('orders/bulk-action/', order_views.order_bulk_action, name='admin_order_bulk_action'),
    path('orders/print/', order_views.order_print_view, name='admin_order_print'),
    
    # Reports
    path('reports/', report_views.reports, name='admin_reports'),
    path('reports/export/', report_views.export_excel, name='admin_reports_export'),

    # Sizes
    path('sizes/', size_views.size_list, name='admin_sizes'),
    path('sizes/create/', size_views.size_create_modal, name='admin_size_create'),
    path('sizes/<int:pk>/edit/', size_views.size_edit_modal, name='admin_size_edit'),
    path('sizes/<int:pk>/update/', size_views.size_update, name='admin_size_update'),
    path('sizes/<int:pk>/delete/', size_views.size_delete, name='admin_size_delete'),
    path('sizes/<int:pk>/toggle/', size_views.size_toggle, name='admin_size_toggle'),
    path('sizes/bulk-action/', size_views.size_bulk_action, name='admin_size_bulk_action'),
]

