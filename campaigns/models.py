from django.db import models
from products.models import Product

class SizeOption(models.Model):
    name = models.CharField(max_length=50, verbose_name="Beden İsmi")
    slug = models.SlugField(unique=True, verbose_name="Slug (Kod)")
    description = models.CharField(max_length=255, blank=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    class Meta:
        verbose_name = "Beden Seçeneği"
        verbose_name_plural = "Beden Seçenekleri"

    def __str__(self):
        return self.name

class Campaign(models.Model):
    title = models.CharField(max_length=255, verbose_name="Kampanya Başlığı")
    slug = models.SlugField(unique=True, verbose_name="Slug (URL)")
    description = models.TextField(blank=True, verbose_name="Açıklama")
    banner_image = models.ImageField(upload_to='campaigns/', blank=True, null=True, verbose_name="Banner Görseli")
    
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Satış Fiyatı")
    min_quantity = models.PositiveIntegerField(default=1, verbose_name="Minimum Adet")
    
    # Financials
    shipping_price = models.DecimalField(max_digits=10, decimal_places=2, default=100, verbose_name="Kargo Ücreti")
    shipping_price_discounted = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="İndirimli Kargo Ücreti")
    cod_price = models.DecimalField(max_digits=10, decimal_places=2, default=100, verbose_name="Kapıda Ödeme Bedeli")
    cod_price_discounted = models.DecimalField(max_digits=10, decimal_places=2, default=85, verbose_name="İndirimli Kapıda Ödeme Bedeli")
    
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")

    available_sizes = models.ManyToManyField(SizeOption, blank=True, verbose_name="Tanımlı Bedenler")

    class Meta:
        verbose_name = "Kampanya"
        verbose_name_plural = "Kampanyalar"

    def __str__(self):
        return self.title

    @property
    def formatted_title(self):
        words = self.title.split()
        if len(words) > 2:
            return f"{' '.join(words[:2])}<br>{' '.join(words[2:])}"
        return self.title

class CampaignProduct(models.Model):
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, verbose_name="Kampanya")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Ürün")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")

    class Meta:
        ordering = ['sort_order']
        verbose_name = "Kampanya Ürünü"
        verbose_name_plural = "Kampanya Ürünleri"

class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Soru")
    answer = models.TextField(verbose_name="Cevap")
    sort_order = models.PositiveIntegerField(default=0, verbose_name="Sıralama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    
    class Meta:
        ordering = ['sort_order']
        verbose_name = "SSS"
        verbose_name_plural = "SSS"
    
    def __str__(self):
        return self.question

