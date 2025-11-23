from django.core.management.base import BaseCommand
from django.utils.text import slugify
from addresses.models import City, District, Neighborhood
from gumbuz_shop.utils.address_data import TURKEY_ADDRESS_DATA


class Command(BaseCommand):
    help = 'Import address data from TURKEY_ADDRESS_DATA'
    
    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Starting address data import...'))
        
        city_count = 0
        district_count = 0
        neighborhood_count = 0
        
        for city_name, districts_data in TURKEY_ADDRESS_DATA.items():
            city, created = City.objects.get_or_create(
                name=city_name,
                defaults={'slug': slugify(city_name)}
            )
            if created:
                city_count += 1
                self.stdout.write(self.style.SUCCESS(f'  Created city: {city_name}'))
            
            for district_name, neighborhoods in districts_data.items():
                district, created = District.objects.get_or_create(
                    city=city,
                    name=district_name,
                    defaults={'slug': slugify(district_name)}
                )
                if created:
                    district_count += 1
                    self.stdout.write(f'    Created district: {district_name}')
                
                for neighborhood_name in neighborhoods:
                    neighborhood, created = Neighborhood.objects.get_or_create(
                        district=district,
                        name=neighborhood_name,
                        defaults={'slug': slugify(neighborhood_name)}
                    )
                    if created:
                        neighborhood_count += 1
        
        self.stdout.write(self.style.SUCCESS('\n=== Import Summary ==='))
        self.stdout.write(self.style.SUCCESS(f'Cities created: {city_count}'))
        self.stdout.write(self.style.SUCCESS(f'Districts created: {district_count}'))
        self.stdout.write(self.style.SUCCESS(f'Neighborhoods created: {neighborhood_count}'))
        self.stdout.write(self.style.SUCCESS('\nSuccessfully imported addresses!'))

