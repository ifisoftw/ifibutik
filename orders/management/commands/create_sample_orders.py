from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Count
from datetime import timedelta, datetime
import random
from orders.models import Order, OrderItem
from campaigns.models import Campaign
from products.models import Product
from addresses.models import City, District, Neighborhood


class Command(BaseCommand):
    help = 'Create sample orders for testing admin panel'
    
    def handle(self, *args, **kwargs):
        # Gerekli verileri al
        campaigns = list(Campaign.objects.filter(is_active=True))
        if not campaigns:
            self.stdout.write(self.style.ERROR('No active campaigns found!'))
            return
        
        cities = list(City.objects.all())
        if not cities:
            self.stdout.write(self.style.ERROR('No cities found!'))
            return
        
        # Örnek müşteri isimleri
        customer_names = [
            ('Ayşe', 'Yılmaz'), ('Fatma', 'Kaya'), ('Zeynep', 'Demir'),
            ('Emine', 'Çelik'), ('Hatice', 'Şahin'), ('Merve', 'Aydın'),
            ('Sema', 'Öztürk'), ('Sibel', 'Arslan'), ('Elif', 'Koç'),
            ('Esra', 'Kurt'), ('Arya', 'Kurdele'), ('Selin', 'Yıldız'),
        ]
        
        address_details = [
            "Atatürk Cad. No:15 Daire:3",
            "İnönü Sok. No:42 Kat:2",
            "Cumhuriyet Mah. 5. Sok. No:18",
            "Yeni Mahalle 123. Sokak No:7 Daire:5",
            "Güneş Apt. Kat:4 No:12",
        ]
        
        size_options = ['36 (S)', '38 (M)', '40 (L)', '42 (XL)', '44 (2XL)', '46 (3XL)']
        cargo_firms = ['NOVA', 'KARGOİST', 'MNG', 'YURTIÇI', 'ARAS']
        
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        orders_created = 0
        
        # BUGÜN için siparişler (24 saate yayılmış)
        self.stdout.write('Creating TODAY orders...')
        for hour in range(24):
            num_orders = random.randint(1, 3)
            
            for _ in range(num_orders):
                campaign = random.choice(campaigns)
                first_name, last_name = random.choice(customer_names)
                phone = f"05{random.randint(300000000, 599999999)}"
                
                city = random.choice(cities)
                districts = list(city.districts.all())
                if not districts:
                    continue
                district = random.choice(districts)
                neighborhoods = list(district.neighborhoods.all())
                if not neighborhoods:
                    continue
                neighborhood = random.choice(neighborhoods)
                
                # Bugün bu saatte
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                created_at = timezone.make_aware(
                    datetime.combine(today, datetime.min.time()) + 
                    timedelta(hours=hour, minutes=minute, seconds=second)
                )
                
                status = random.choices(
                    ['new', 'processing', 'shipped', 'delivered', 'cancelled'],
                    weights=[0.3, 0.3, 0.2, 0.15, 0.05]
                )[0]
                
                order = self._create_order(
                    campaign, f"{first_name} {last_name}", phone,
                    city, district, neighborhood, address_details,
                    status, created_at, cargo_firms, size_options
                )
                
                if order:
                    orders_created += 1
        
        today_count = orders_created
        self.stdout.write(self.style.SUCCESS(f'Created {today_count} orders for TODAY'))
        
        # DÜN için siparişler (24 saate yayılmış)
        self.stdout.write('Creating YESTERDAY orders...')
        for hour in range(24):
            num_orders = random.randint(1, 2)
            
            for _ in range(num_orders):
                campaign = random.choice(campaigns)
                first_name, last_name = random.choice(customer_names)
                phone = f"05{random.randint(300000000, 599999999)}"
                
                city = random.choice(cities)
                districts = list(city.districts.all())
                if not districts:
                    continue
                district = random.choice(districts)
                neighborhoods = list(district.neighborhoods.all())
                if not neighborhoods:
                    continue
                neighborhood = random.choice(neighborhoods)
                
                # Dün bu saatte
                minute = random.randint(0, 59)
                second = random.randint(0, 59)
                created_at = timezone.make_aware(
                    datetime.combine(yesterday, datetime.min.time()) + 
                    timedelta(hours=hour, minutes=minute, seconds=second)
                )
                
                # Dün için daha çok tamamlanmış siparişler
                status = random.choices(
                    ['delivered', 'shipped', 'processing', 'new', 'cancelled'],
                    weights=[0.5, 0.2, 0.15, 0.1, 0.05]
                )[0]
                
                order = self._create_order(
                    campaign, f"{first_name} {last_name}", phone,
                    city, district, neighborhood, address_details,
                    status, created_at, cargo_firms, size_options
                )
                
                if order:
                    orders_created += 1
        
        yesterday_count = orders_created - today_count
        self.stdout.write(self.style.SUCCESS(f'Created {yesterday_count} orders for YESTERDAY'))
        
        self.stdout.write(self.style.SUCCESS(f'\n=== Total: {orders_created} orders created! ==='))
        self.stdout.write('\nStatus breakdown:')
        for status_data in Order.objects.values('status').annotate(count=Count('id')).order_by('-count'):
            self.stdout.write(f"  - {status_data['status']}: {status_data['count']}")
    
    def _create_order(self, campaign, customer_name, phone, city, district, neighborhood, 
                      address_details, status, created_at, cargo_firms, size_options):
        """Helper method to create an order"""
        try:
            address_detail = random.choice(address_details)
            full_address = f"{neighborhood.name} Mah. {address_detail}"
            
            order = Order.objects.create(
                campaign=campaign,
                status=status,
                customer_name=customer_name,
                phone=phone,
                city_fk=city,
                district_fk=district,
                neighborhood_fk=neighborhood,
                city=city.name,
                district=district.name,
                full_address=full_address,
                campaign_price=campaign.price,
                cargo_price=campaign.shipping_price,
                cod_fee=campaign.cod_price,
                total_amount=campaign.price + campaign.cod_price,
            )
            # Update created_at bypassing auto_now_add
            Order.objects.filter(pk=order.pk).update(created_at=created_at)
            
            # Kargo bilgileri (shipped/delivered için)
            if status in ['shipped', 'delivered']:
                order.cargo_firm = random.choice(cargo_firms)
                order.tracking_code = str(random.randint(1000000000, 9999999999))
                order.cargo_barcode = order.tracking_code
                order.save()
            
            # Sipariş kalemleri
            campaign_products = list(campaign.campaignproduct_set.select_related('product').all())
            if campaign_products:
                selected_products = random.sample(
                    campaign_products, 
                    min(campaign.min_quantity, len(campaign_products))
                )
                
                selected_size = random.choice(size_options)
                
                for cp in selected_products:
                    OrderItem.objects.create(
                        order=order,
                        product=cp.product,
                        quantity=1,
                        selected_size=selected_size
                    )
            
            return order
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Error creating order: {e}'))
            return None
