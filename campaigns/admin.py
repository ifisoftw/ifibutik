from django.contrib import admin
from .models import Campaign, CampaignProduct, SizeOption

class CampaignProductInline(admin.TabularInline):
    model = CampaignProduct
    extra = 1
    fields = ('product', 'sort_order')

@admin.register(SizeOption)
class SizeOptionAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'min_quantity')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CampaignProductInline]
    filter_horizontal = ('available_sizes',)
