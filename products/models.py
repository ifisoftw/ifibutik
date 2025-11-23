from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name="Ürün Adı")
    sku = models.CharField(max_length=100, unique=True, verbose_name="Stok Kodu (SKU)")
    description = models.TextField(blank=True, null=True, verbose_name="Açıklama")
    is_active = models.BooleanField(default=True, verbose_name="Aktif mi?")
    stock_qty = models.IntegerField(default=0, verbose_name="Stok Adedi")

    class Meta:
        verbose_name = "Ürün"
        verbose_name_plural = "Ürünler"

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="Ürün")
    image = models.ImageField(upload_to='products/', verbose_name="Görsel")
    sort_order = models.IntegerField(default=0, verbose_name="Sıralama")

    class Meta:
        ordering = ['sort_order']
        verbose_name = "Ürün Görseli"
        verbose_name_plural = "Ürün Görselleri"

    def __str__(self):
        return f"{self.product.name} Görseli"
