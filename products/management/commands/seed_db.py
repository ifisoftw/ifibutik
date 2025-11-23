from django.core.management.base import BaseCommand
from products.models import Product, ProductImage
from campaigns.models import Campaign, CampaignProduct, SizeOption
from orders.models import Order, OrderItem
from django.core.files.base import ContentFile
from django.utils.text import slugify
import requests
import random
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Populates the database with dummy data'

    def handle(self, *args, **kwargs):
        self.stdout.write('Cleaning old data...')
        Order.objects.all().delete()
        Campaign.objects.all().delete()
        Product.objects.all().delete()
        SizeOption.objects.all().delete()

        self.stdout.write('Creating Size Options...')
        sizes = [
            ("36 (S)", "36-s", "Bel: 34cm, Basen: 90cm"),
            ("38 (M)", "38-m", "Bel: 36cm, Basen: 94cm"),
            ("40 (L)", "40-l", "Bel: 38cm, Basen: 98cm"),
            ("42 (XL)", "42-xl", "Bel: 40cm, Basen: 102cm"),
            ("44 (XXL)", "44-xxl", "Bel: 42cm, Basen: 106cm"),
        ]
        
        size_objects = []
        for name, slug, desc in sizes:
            size = SizeOption.objects.create(name=name, slug=slug, description=desc)
            size_objects.append(size)

        self.stdout.write('Downloading placeholder images...')
        # Using picsum for random fashion-like images
        def get_image():
            response = requests.get(f'https://picsum.photos/800/800?random={random.randint(1, 1000)}')
            if response.status_code == 200:
                return ContentFile(response.content)
            return None

        self.stdout.write('Creating Products...')
        products = []
        product_names = [
            "İpek Şal", "Pamuklu Tunik", "Kot Etek", "Keten Pantolon", "Desenli Elbise",
            "Triko Kazak", "Deri Çanta", "Spor Ayakkabı", "Klasik Gömlek", "Yazlık Bluz"
        ]

        for i, name in enumerate(product_names):
            p = Product.objects.create(
                name=name,
                sku=f"SKU-{random.randint(1000, 9999)}",
                description=f"{name} harika bir ürün. %100 kaliteli kumaştan üretilmiştir.",
                stock_qty=random.randint(10, 100),
                is_active=True
            )
            products.append(p)
            
            # Add 2-3 images per product
            for j in range(random.randint(2, 3)):
                img_content = get_image()
                if img_content:
                    img_content.name = f"{slugify(name)}_{j}.jpg"
                    ProductImage.objects.create(
                        product=p,
                        image=img_content,
                        sort_order=j
                    )

        self.stdout.write('Creating Campaigns...')
        campaign_data = [
            {
                "title": "3 ADET TESETTÜR ALT-ÜST TAKIM",
                "price": 1899.00,
                "min_qty": 3
            },
            {
                "title": "3 ADET TESETTÜR TUNİK",
                "price": 1499.00,
                "min_qty": 3
            }
        ]

        created_campaigns = []
        for data in campaign_data:
            c = Campaign.objects.create(
                title=data["title"],
                slug=slugify(data["title"]),
                description="Bu kampanya ile harika kombinler yapabilirsiniz. Sınırlı stok!",
                price=data["price"],
                min_quantity=data["min_qty"],
                shipping_price=50.00,
                cod_price=29.90
            )
            
            # Add banner
            banner_content = get_image()
            if banner_content:
                c.banner_image.save(f"banner_{c.slug}.jpg", banner_content)
                c.save()

            # Add random products to campaign
            selected_products = random.sample(products, 5)
            for idx, prod in enumerate(selected_products):
                CampaignProduct.objects.create(
                    campaign=c,
                    product=prod,
                    sort_order=idx
                )

            # Add all sizes to campaign
            c.available_sizes.set(size_objects)
            created_campaigns.append(c)

        self.stdout.write('Creating Orders...')
        statuses = ['new', 'processing', 'shipped', 'delivered', 'cancelled']
        
        for i in range(15):
            campaign = random.choice(created_campaigns)
            order = Order.objects.create(
                campaign=campaign,
                customer_name=f"Müşteri {i+1}",
                phone=f"555{random.randint(1000000, 9999999)}",
                city="İstanbul",
                district="Kadıköy",
                full_address="Örnek Mahallesi, Örnek Sokak No:1",
                status=random.choice(statuses),
                total_amount=campaign.price + campaign.cod_price,
                created_at=timezone.now() - timedelta(days=random.randint(0, 7))
            )
            
            # Add items
            campaign_products = campaign.campaignproduct_set.all()
            for cp in campaign_products[:campaign.min_quantity]:
                OrderItem.objects.create(
                    order=order,
                    product=cp.product,
                    quantity=1,
                    selected_size="38 (M)"
                )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
