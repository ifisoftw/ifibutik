from django.db import models
from django.contrib.auth.models import User


class AdminRole(models.Model):
    """Rol modeli - Süper Admin, Admin, Editör, Görüntüleyici"""
    ROLE_CHOICES = [
        ('super_admin', 'Süper Admin'),
        ('admin', 'Admin'),
        ('editor', 'Editör'),
        ('viewer', 'Görüntüleyici'),
    ]
    
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True, verbose_name='Rol Adı')
    description = models.TextField(blank=True, verbose_name='Açıklama')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    
    class Meta:
        verbose_name = 'Admin Rolü'
        verbose_name_plural = 'Admin Rolleri'
    
    def __str__(self):
        return self.get_name_display()


class AdminPermission(models.Model):
    """İzin modeli - Hangi role hangi izinler verilmiş"""
    PERMISSION_CHOICES = [
        ('view_dashboard', 'Dashboard Görüntüleme'),
        ('manage_campaigns', 'Kampanya Yönetimi'),
        ('manage_products', 'Ürün Yönetimi'),
        ('manage_orders', 'Sipariş Yönetimi'),
        ('view_reports', 'Rapor Görüntüleme'),
        ('export_data', 'Veri Export'),
        ('manage_users', 'Kullanıcı Yönetimi'),
        ('manage_settings', 'Ayar Yönetimi'),
    ]
    
    role = models.ForeignKey(AdminRole, on_delete=models.CASCADE, related_name='permissions', verbose_name='Rol')
    permission = models.CharField(max_length=50, choices=PERMISSION_CHOICES, verbose_name='İzin')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    
    class Meta:
        verbose_name = 'Admin İzni'
        verbose_name_plural = 'Admin İzinleri'
        unique_together = [['role', 'permission']]
    
    def __str__(self):
        return f"{self.role.get_name_display()} - {self.get_permission_display()}"


class AdminUser(models.Model):
    """Admin kullanıcı profili"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Kullanıcı', related_name='admin_profile')
    role = models.ForeignKey(AdminRole, on_delete=models.PROTECT, verbose_name='Rol')
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Telefon')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Güncellenme Tarihi')
    
    class Meta:
        verbose_name = 'Admin Kullanıcı'
        verbose_name_plural = 'Admin Kullanıcılar'
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role.get_name_display()})"
    
    def has_permission(self, permission_code):
        """Kullanıcının belirli bir izni olup olmadığını kontrol et"""
        return self.role.permissions.filter(permission=permission_code).exists()


class SiteSettings(models.Model):
    # Store Info
    store_name = models.CharField(max_length=255, default="Gumbuz Butik", verbose_name="Mağaza Adı")
    store_slogan = models.CharField(max_length=255, blank=True, verbose_name="Mağaza Sloganı")
    store_description = models.TextField(blank=True, verbose_name="Mağaza Açıklaması")
    store_logo = models.ImageField(upload_to='settings/', blank=True, verbose_name="Mağaza Logosu")
    
    # Contact
    whatsapp_number = models.CharField(max_length=20, blank=True, verbose_name="WhatsApp Numarası")
    instagram_url = models.URLField(blank=True, verbose_name="Instagram Profili")
    facebook_url = models.URLField(blank=True, verbose_name="Facebook Sayfası")
    
    # Integrations
    gtm_id = models.CharField(max_length=50, blank=True, verbose_name="Google Tag Manager ID")
    ga4_id = models.CharField(max_length=50, blank=True, verbose_name="Google Analytics 4 ID")
    pixel_id = models.CharField(max_length=50, blank=True, verbose_name="Meta Pixel ID")
    hotjar_id = models.CharField(max_length=50, blank=True, verbose_name="Hotjar ID")
    contentsquare_id = models.CharField(max_length=50, blank=True, verbose_name="ContentSquare ID")
    onesignal_app_id = models.CharField(max_length=100, blank=True, verbose_name="OneSignal App ID")
    facebook_domain_verification = models.CharField(max_length=100, blank=True, verbose_name="Facebook Domain Verification")

    # Security
    rate_limit_count = models.PositiveIntegerField(default=5, verbose_name="Rate Limit (Adet)")
    rate_limit_period = models.PositiveIntegerField(default=600, verbose_name="Rate Limit Süresi (Saniye)")

    class Meta:
        verbose_name = 'Site Ayarları'
        verbose_name_plural = 'Site Ayarları'

    def save(self, *args, **kwargs):
        self.pk = 1  # Singleton pattern
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return "Site Ayarları"


class FAQ(models.Model):
    """Sıkça Sorulan Sorular"""
    question = models.CharField(max_length=255, verbose_name="Soru")
    answer = models.TextField(verbose_name="Cevap")
    order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = 'SSS'
        verbose_name_plural = 'SSS'
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.question

