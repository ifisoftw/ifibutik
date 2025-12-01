from django.db import models
from products.models import Product
from addresses.models import City, District, Neighborhood

class Order(models.Model):
    STATUS_CHOICES = (
        ('new', 'Yeni Sipariş'),
        ('processing', 'İşleme Alındı'),
        ('shipped', 'Kargolandı'),
        ('delivered', 'Teslim Edildi'),
        ('cancelled', 'İptal'),
        ('return', 'İade'),
    )

    campaign = models.ForeignKey('campaigns.Campaign', on_delete=models.SET_NULL, null=True, verbose_name="Satın Alınan Kampanya")
    
    # Snapshot Fields (Kampanya)
    campaign_title = models.CharField(max_length=255, blank=True, null=True, verbose_name="Kampanya Başlığı (Snapshot)")
    campaign_slug = models.SlugField(max_length=255, blank=True, null=True, verbose_name="Kampanya Slug (Snapshot)")
    campaign_image_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="Kampanya Görsel URL (Snapshot)")

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new', verbose_name="Durum")
    
    customer_name = models.CharField(max_length=255, verbose_name="Müşteri Adı")
    phone = models.CharField(max_length=20, verbose_name="Telefon")
    
    # Address ForeignKeys (yeni)
    city_fk = models.ForeignKey(City, on_delete=models.PROTECT, null=True, blank=True, related_name='orders', verbose_name="İl")
    district_fk = models.ForeignKey(District, on_delete=models.PROTECT, null=True, blank=True, related_name='orders', verbose_name="İlçe")
    neighborhood_fk = models.ForeignKey(Neighborhood, on_delete=models.PROTECT, null=True, blank=True, related_name='orders', verbose_name="Mahalle")
    
    # Address text fields (backward compatibility için)
    city = models.CharField(max_length=100, verbose_name="İl", blank=True)
    district = models.CharField(max_length=100, verbose_name="İlçe", blank=True)
    full_address = models.TextField(verbose_name="Tam Adres")

    # Finansal Bilgiler
    campaign_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Kampanya Fiyatı")
    cargo_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Kargo Ücreti")
    cod_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Kapıda Ödeme Bedeli")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Toplam Tutar")

    # Sipariş Takip
    tracking_number = models.CharField(max_length=10, unique=True, null=True, blank=True, verbose_name="Sipariş Takip Numarası")
    
    # Kargo Entegrasyonu
    cargo_firm = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kargo Firması")
    tracking_code = models.CharField(max_length=100, blank=True, null=True, verbose_name="Takip Kodu")
    cargo_barcode = models.CharField(max_length=100, blank=True, null=True, verbose_name="Kargo Barkod")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Güncellenme Tarihi")

    class Meta:
        verbose_name = "Sipariş"
        verbose_name_plural = "Siparişler"

    def __str__(self):
        return f"Sipariş #{self.id} - {self.customer_name}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Sipariş")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün")
    quantity = models.IntegerField(default=1, verbose_name="Adet")
    selected_size = models.CharField(max_length=50, blank=True, null=True, verbose_name="Seçilen Beden")
    selected_size_name = models.CharField(max_length=50, blank=True, null=True, verbose_name="Beden İsmi")
    selected_size_description = models.CharField(max_length=255, blank=True, null=True, verbose_name="Beden Açıklaması")
    
    # Snapshot Fields (Sipariş anındaki bilgiler)
    product_name = models.CharField(max_length=255, blank=True, null=True, verbose_name="Ürün Adı (Snapshot)")
    product_sku = models.CharField(max_length=100, blank=True, null=True, verbose_name="SKU (Snapshot)")
    product_description = models.TextField(blank=True, null=True, verbose_name="Açıklama (Snapshot)")
    product_image_url = models.CharField(max_length=500, blank=True, null=True, verbose_name="Görsel URL (Snapshot)")

    class Meta:
        verbose_name = "Sipariş Ürünü"
        verbose_name_plural = "Sipariş Ürünleri"

    def __str__(self):
        return f"{self.quantity}x {self.product.name} - Sipariş #{self.order.id}"
