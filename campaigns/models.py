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
        from django.utils.html import escape
        words = self.title.split()
        if len(words) > 2:
            return f"{escape(' '.join(words[:2]))}<br>{escape(' '.join(words[2:]))}"
        return escape(self.title)

    @property
    def unit_price(self):
        if self.min_quantity > 0:
            return self.price / self.min_quantity
        return 0
    
    def save(self, *args, **kwargs):
        # Store old slug if this is an update
        old_slug = None
        old_title = None
        if self.pk:  # Sadece mevcut kayıtlar için
            try:
                old_instance = Campaign.objects.get(pk=self.pk)
                # Slug değişti mi?
                if old_instance.slug != self.slug:
                    old_slug = old_instance.slug
                    old_title = old_instance.title
            except Campaign.DoesNotExist:
                pass
        
        # First save the campaign with new slug
        super().save(*args, **kwargs)
        
        # Clean up redirects to prevent loops
        if old_slug and old_slug != self.slug:
            # If new slug matches any existing redirect's old_slug, delete that redirect
            # This prevents: A->B exists, then changing B back to A (which would create B->A loop)
            CampaignRedirect.objects.filter(
                old_slug=self.slug,
                campaign=self
            ).delete()
            
            # Create new redirect from old slug to new slug
            CampaignRedirect.objects.create(
                old_slug=old_slug,
                campaign=self,
                old_title=old_title,
                is_manual=False
            )


class CampaignRedirect(models.Model):
    old_slug = models.SlugField(max_length=255, unique=True, verbose_name="Eski Slug")
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='redirects', verbose_name="Hedef Kampanya")
    old_title = models.CharField(max_length=255, blank=True, verbose_name="Eski Başlık")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")
    is_manual = models.BooleanField(default=False, verbose_name="Manuel Eklendi")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Oluşturulma Tarihi")
    
    class Meta:
        verbose_name = "Kampanya Yönlendirmesi"
        verbose_name_plural = "Kampanya Yönlendirmeleri"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.old_slug} → {self.campaign.slug}"


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

