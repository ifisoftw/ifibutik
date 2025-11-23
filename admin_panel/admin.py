from django.contrib import admin
from .models import AdminRole, AdminPermission, AdminUser


class AdminPermissionInline(admin.TabularInline):
    model = AdminPermission
    extra = 0
    fields = ['permission']


@admin.register(AdminRole)
class AdminRoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'description', 'permission_count', 'created_at']
    list_filter = ['name', 'created_at']
    search_fields = ['name', 'description']
    inlines = [AdminPermissionInline]
    
    def permission_count(self, obj):
        return obj.permissions.count()
    permission_count.short_description = 'İzin Sayısı'


@admin.register(AdminUser)
class AdminUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'role', 'is_active', 'phone', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'phone']
    raw_id_fields = ['user']
    
    fieldsets = (
        ('Kullanıcı Bilgileri', {
            'fields': ('user', 'role', 'is_active')
        }),
        ('İletişim', {
            'fields': ('phone',)
        }),
        ('Tarihler', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']

