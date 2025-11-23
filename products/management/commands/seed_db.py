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
            ("46 (3XL)", "46-3xl", "Bel: 44cm, Basen: 110cm"),
        ]
        
        size_objects = []
        for name, slug, desc in sizes:
            size = SizeOption.objects.create(name=name, slug=slug, description=desc)
            size_objects.append(size)

        self.stdout.write('Downloading placeholder images...')
        # Using loremflickr for specific keywords
        def get_image(keywords="hijab,dress"):
            try:
                # Adding a random parameter to avoid caching and get different images
                response = requests.get(f'https://loremflickr.com/800/800/{keywords}?random={random.randint(1, 1000)}', timeout=10)
                if response.status_code == 200:
                    return ContentFile(response.content)
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"Could not download image: {e}"))
            return None

        self.stdout.write('Creating Products...')
        products = []
        product_data = [
            ("Siyah Ferace", "ferace,black"),
            ("Çiçekli Tesettür Elbise", "dress,floral"),
            ("Pileli Etek", "skirt,pleated"),
            ("Oversize Tunik", "tunic,fashion"),
            ("İpek Eşarp", "scarf,silk"),
            ("Pamuklu Şal", "shawl,cotton"),
            ("Kuşaklı Trençkot", "trenchcoat,fashion"),
            ("Bol Paça Pantolon", "pants,wideleg"),
            ("Abaya", "abaya,black"),
            ("Uzun Hırka", "cardigan,long"),
            ("Kot Elbise", "denim,dress"),
            ("Keten Takım", "linen,suit"),
        ]

        for i, (name, keywords) in enumerate(product_data):
            p = Product.objects.create(
                name=name,
                sku=f"SKU-{random.randint(1000, 9999)}",
                description=f"{name} harika bir ürün. %100 kaliteli kumaştan üretilmiştir. Tesettür giyim modasına uygundur.",
                stock_qty=random.randint(10, 100),
                is_active=True
            )
            products.append(p)
            
            # Add 2-3 images per product
            self.stdout.write(f"  Downloading images for {name}...")
            for j in range(random.randint(2, 3)):
                img_content = get_image(keywords)
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
                "min_qty": 3,
                "keywords": "suit,hijab"
            },
            {
                "title": "3 ADET TESETTÜR TUNİK KAMPANYASI",
                "price": 1499.00,
                "min_qty": 3,
                "keywords": "tunic,hijab"
            },
            {
                "title": "2'Lİ ABAYA FIRSATI",
                "price": 2500.00,
                "min_qty": 2,
                "keywords": "abaya"
            }
        ]

        created_campaigns = []
        for data in campaign_data:
            c = Campaign.objects.create(
                title=data["title"],
                slug=slugify(data["title"]),
                description="Bu kampanya ile harika kombinler yapabilirsiniz. Sınırlı stok! Sezonun en trend parçaları.",
                price=data["price"],
                min_quantity=data["min_qty"],
                shipping_price=50.00,
                cod_price=29.90
            )
            
            # Add banner
            self.stdout.write(f"  Downloading banner for {data['title']}...")
            banner_content = get_image(data.get("keywords", "fashion"))
            if banner_content:
                c.banner_image.save(f"banner_{c.slug}.jpg", banner_content)
                c.save()

            # Add random products to campaign
            # Try to match products somewhat if possible, but random is fine for now
            selected_products = random.sample(products, min(len(products), 6))
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
            # Add items up to min_quantity or more
            items_to_add = campaign_products[:campaign.min_quantity]
            if not items_to_add:
                 items_to_add = campaign_products # Fallback
            
            for cp in items_to_add:
                OrderItem.objects.create(
                    order=order,
                    product=cp.product,
                    quantity=1,
                    selected_size="38 (M)"
                )

        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
