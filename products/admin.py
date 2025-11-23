from django.contrib import admin
from .models import Product, ProductImage

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'sku', 'stock_qty', 'is_active')
    search_fields = ('name', 'sku')
    list_filter = ('is_active',)
    inlines = [ProductImageInline]
