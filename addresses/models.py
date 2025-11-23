from django.db import models
from django.utils.text import slugify


class City(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='İl Adı')
    slug = models.SlugField(max_length=100, unique=True)
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    
    class Meta:
        ordering = ['name']
        verbose_name = 'İl'
        verbose_name_plural = 'İller'
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class District(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='districts', verbose_name='İl')
    name = models.CharField(max_length=100, verbose_name='İlçe Adı')
    slug = models.SlugField(max_length=100)
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    
    class Meta:
        ordering = ['name']
        unique_together = [['city', 'name']]
        verbose_name = 'İlçe'
        verbose_name_plural = 'İlçeler'
    
    def __str__(self):
        return f"{self.city.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Neighborhood(models.Model):
    district = models.ForeignKey(District, on_delete=models.CASCADE, related_name='neighborhoods', verbose_name='İlçe')
    name = models.CharField(max_length=100, verbose_name='Mahalle Adı')
    slug = models.SlugField(max_length=100)
    is_active = models.BooleanField(default=True, verbose_name='Aktif')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Oluşturulma Tarihi')
    
    class Meta:
        ordering = ['name']
        unique_together = [['district', 'name']]
        verbose_name = 'Mahalle'
        verbose_name_plural = 'Mahalleler'
    
    def __str__(self):
        return f"{self.district.city.name} - {self.district.name} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

