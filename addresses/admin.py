from django.contrib import admin
from .models import City, District, Neighborhood


class DistrictInline(admin.TabularInline):
    model = District
    extra = 0
    fields = ['name', 'slug', 'is_active']
    readonly_fields = ['name', 'slug']
    can_delete = False


class NeighborhoodInline(admin.TabularInline):
    model = Neighborhood
    extra = 0
    fields = ['name', 'slug', 'is_active']
    readonly_fields = ['name', 'slug']
    can_delete = False


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'district_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name']
    readonly_fields = ['name', 'slug', 'created_at']
    inlines = [DistrictInline]
    
    def district_count(self, obj):
        return obj.districts.count()
    district_count.short_description = 'İlçe Sayısı'
    
    def has_add_permission(self, request):
        # Yeni il eklenmesini engelle (data import ile yapılacak)
        return False


@admin.register(District)
class DistrictAdmin(admin.ModelAdmin):
    list_display = ['name', 'city', 'neighborhood_count', 'is_active', 'created_at']
    list_filter = ['city', 'is_active', 'created_at']
    search_fields = ['name', 'city__name']
    readonly_fields = ['name', 'slug', 'city', 'created_at']
    inlines = [NeighborhoodInline]
    
    def neighborhood_count(self, obj):
        return obj.neighborhoods.count()
    neighborhood_count.short_description = 'Mahalle Sayısı'
    
    def has_add_permission(self, request):
        # Yeni ilçe eklenmesini engelle (data import ile yapılacak)
        return False


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'district', 'get_city', 'is_active', 'created_at']
    list_filter = ['district__city', 'is_active', 'created_at']
    search_fields = ['name', 'district__name', 'district__city__name']
    readonly_fields = ['name', 'slug', 'district', 'created_at']
    
    def get_city(self, obj):
        return obj.district.city.name
    get_city.short_description = 'İl'
    get_city.admin_order_field = 'district__city__name'
    
    def has_add_permission(self, request):
        # Yeni mahalle eklenmesini engelle (data import ile yapılacak)
        return False

