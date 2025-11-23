from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_name', 'phone', 'status', 'city', 'total_amount', 'created_at')
    list_filter = ('status', 'city', 'campaign')
    search_fields = ('customer_name', 'phone', 'tracking_code')
    inlines = [OrderItemInline]
