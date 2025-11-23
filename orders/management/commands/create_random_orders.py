from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import random
from decimal import Decimal

from orders.models import Order, OrderItem
from campaigns.models import Campaign, CampaignProduct
from addresses.models import City, District, Neighborhood


class Command(BaseCommand):
    help = 'Son 1 hafta için rastgele siparişler oluşturur'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=30,
            help='Oluşturulacak sipariş sayısı (varsayılan: 30)'
        )

    def handle(self, *args, **options):
        count = options['count']
        
        # Türk isimleri - gerçekçi kombinasyonlar
        first_names = [
            'Ahmet', 'Mehmet', 'Mustafa', 'Ali', 'Hüseyin', 'Hasan', 'İbrahim', 'Ömer', 
            'Fatma', 'Ayşe', 'Emine', 'Hatice', 'Zeynep', 'Elif', 'Meryem', 'Fadime',
            'Burak', 'Can', 'Emre', 'Cem', 'Deniz', 'Ege', 'Kaan', 'Berk',
            'Selin', 'Ebru', 'Merve', 'Gizem', 'Nur', 'Damla', 'İrem', 'Ceren',
            'Kerem', 'Mert', 'Onur', 'Barış', 'Serkan', 'Tolga', 'Volkan',
            'Şeyma', 'Tuğba', 'Seda', 'Derya', 'Burcu', 'Dilek', 'Özlem'
        ]
        
        last_names = [
            'Yılmaz', 'Kaya', 'Demir', 'Çelik', 'Şahin', 'Yıldız', 'Yıldırım', 'Öztürk',
            'Aydın', 'Özdemir', 'Arslan', 'Doğan', 'Kılıç', 'Aslan', 'Çetin', 'Kara',
            'Koç', 'Kurt', 'Özkan', 'Şimşek', 'Erdoğan', 'Polat', 'Aksoy', 'Korkmaz',
            'Türk', 'Acar', 'Güneş', 'Başar', 'Bozkurt', 'Tekin', 'Karaca', 'Özer',
            'Taş', 'Çakır', 'Ateş', 'Bulut', 'Duman', 'Erdem', 'Turan', 'Ak'
        ]

        # Telefon numaraları için gerçek operatör kodları
        phone_operators = ['530', '531', '532', '533', '534', '535', '536', '537', '538', '539',
                          '541', '542', '543', '544', '545', '546', '547', '548', '549',
                          '501', '505', '506', '507', '508', '509', 
                          '551', '552', '553', '554', '555', '556', '559']

        # Sipariş statusları ve ağırlıkları
        statuses = [
            ('new', 20),         # %20 yeni
            ('processing', 30),  # %30 işlemde
            ('shipped', 35),     # %35 kargolandı
            ('delivered', 10),   # %10 teslim edildi
            ('cancelled', 3),    # %3 iptal
            ('return', 2),       # %2 iade
        ]
        status_list = []
        for status, weight in statuses:
            status_list.extend([status] * weight)

        # Kargo firmaları
        cargo_firms = ['MNG Kargo', 'Yurtiçi Kargo', 'Aras Kargo', 'PTT Kargo', 'Sürat Kargo']

        # Veritabanından verileri çek
        campaigns = list(Campaign.objects.filter(is_active=True))
        cities = list(City.objects.filter(is_active=True))
        
        if not campaigns:
            self.stdout.write(self.style.ERROR('Aktif kampanya bulunamadı!'))
            return
        
        if not cities:
            self.stdout.write(self.style.ERROR('Aktif şehir bulunamadı!'))
            return

        self.stdout.write(self.style.SUCCESS(f'{count} adet sipariş oluşturuluyor...'))
        
        created_count = 0
        now = timezone.now()
        
        for i in range(count):
            try:
                # Rastgele müşteri bilgileri
                customer_name = f"{random.choice(first_names)} {random.choice(last_names)}"
                phone = f"0{random.choice(phone_operators)} {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
                
                # Rastgele adres bilgileri
                city = random.choice(cities)
                districts = list(city.districts.filter(is_active=True))
                if not districts:
                    continue
                    
                district = random.choice(districts)
                neighborhoods = list(district.neighborhoods.filter(is_active=True))
                if not neighborhoods:
                    continue
                    
                neighborhood = random.choice(neighborhoods)
                
                # Rastgele sokak isimleri
                streets = [
                    'Atatürk Caddesi', 'İstiklal Caddesi', 'Cumhuriyet Caddesi', 
                    'Gazi Bulvarı', 'Ankara Caddesi', 'İzmir Caddesi',
                    'Fatih Sokak', 'Mehmet Sokak', 'Ali Sokak', 'Veli Sokak',
                    'Yaşar Sokak', 'Kemal Sokak', 'Zafer Sokak', 'Hürriyet Caddesi'
                ]
                
                building_no = random.randint(1, 250)
                apartment_no = random.randint(1, 30)
                
                full_address = f"{neighborhood.name} Mahallesi, {random.choice(streets)} No: {building_no}/{apartment_no}, {district.name}/{city.name}"
                
                # Rastgele kampanya seç
                campaign = random.choice(campaigns)
                
                # Finansal bilgiler
                campaign_price = campaign.price
                
                # Kargo ve kapıda ödeme için indirimli fiyat kullanma şansı
                if random.random() < 0.7:  # %70 ihtimalle indirimli
                    cargo_price = campaign.shipping_price_discounted
                    cod_fee = campaign.cod_price_discounted
                else:
                    cargo_price = campaign.shipping_price
                    cod_fee = campaign.cod_price
                
                total_amount = campaign_price + cargo_price + cod_fee
                
                # Rastgele status
                status = random.choice(status_list)
                
                # Kargo bilgileri (eğer kargoya verilmişse)
                cargo_firm = None
                tracking_code = None
                cargo_barcode = None
                
                if status in ['shipped', 'delivered']:
                    cargo_firm = random.choice(cargo_firms)
                    tracking_code = f"{random.randint(1000000000, 9999999999)}"
                    cargo_barcode = f"BR{random.randint(100000000, 999999999)}"
                
                # Rastgele tarih - son 7 gün içinde
                days_ago = random.randint(0, 7)
                hours = random.randint(8, 22)  # 08:00 - 22:00 arası
                minutes = random.randint(0, 59)
                seconds = random.randint(0, 59)
                
                created_date = now - timedelta(
                    days=days_ago,
                    hours=(now.hour - hours),
                    minutes=(now.minute - minutes),
                    seconds=(now.second - seconds)
                )
                
                # Sipariş oluştur
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
                    campaign_price=campaign_price,
                    cargo_price=cargo_price,
                    cod_fee=cod_fee,
                    total_amount=total_amount,
                    cargo_firm=cargo_firm,
                    tracking_code=tracking_code,
                    cargo_barcode=cargo_barcode,
                )
                
                # created_at tarihini manuel olarak güncelle
                Order.objects.filter(id=order.id).update(
                    created_at=created_date,
                    updated_at=created_date
                )
                
                # Kampanyaya ait ürünleri al
                campaign_products = CampaignProduct.objects.filter(campaign=campaign).select_related('product')
                
                if campaign_products.exists():
                    # Her üründen 1 adet OrderItem oluştur
                    for cp in campaign_products:
                        # Rastgele beden seç (eğer kampanyada bedenler varsa)
                        selected_size = None
                        available_sizes = list(campaign.available_sizes.filter(is_active=True))
                        if available_sizes:
                            selected_size = random.choice(available_sizes).name
                        
                        OrderItem.objects.create(
                            order=order,
                            product=cp.product,
                            quantity=1,
                            selected_size=selected_size
                        )
                
                created_count += 1
                
                if (i + 1) % 10 == 0:
                    self.stdout.write(self.style.SUCCESS(f'{i + 1} sipariş oluşturuldu...'))
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Sipariş oluşturulurken hata: {str(e)}'))
                continue
        
        self.stdout.write(self.style.SUCCESS(f'Toplam {created_count} adet sipariş başarıyla oluşturuldu!'))
        
        # İstatistikleri göster
        status_counts = {}
        for order in Order.objects.all():
            status_counts[order.get_status_display()] = status_counts.get(order.get_status_display(), 0) + 1
        
        self.stdout.write(self.style.SUCCESS('\n=== Sipariş Durum İstatistikleri ==='))
        for status_name, count in status_counts.items():
            self.stdout.write(f'{status_name}: {count} adet')

