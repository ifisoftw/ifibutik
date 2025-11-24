import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gumbuz_shop.settings')
django.setup()

from products.models import Product

description = """Kapüşonlu Tunik Boy: 70 CM
Çimalı Pantolon Boy: 100 CM
[İki İplik Kumaş] [Cep Mevcut]
Kapıda ödeme için aşağı kaydırın."""

count = Product.objects.update(description=description)
print(f"Updated {count} products.")
