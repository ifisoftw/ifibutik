from django.contrib import admin
from .models import Campaign, SizeOption, CampaignProduct, FAQ

class CampaignProductInline(admin.TabularInline):
    model = CampaignProduct
    extra = 1
    fields = ('product', 'sort_order')

@admin.register(SizeOption)
class SizeOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    list_filter = ['is_active']
    search_fields = ['name', 'slug']

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'sort_order', 'is_active']
    list_editable = ['sort_order', 'is_active']
    list_filter = ['is_active']
    search_fields = ['question', 'answer']

@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'min_quantity')
    search_fields = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    inlines = [CampaignProductInline]
    filter_horizontal = ('available_sizes',)
