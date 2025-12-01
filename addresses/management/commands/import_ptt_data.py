import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from addresses.models import City, District, Neighborhood
from django.db import transaction

from slugify import slugify

class Command(BaseCommand):
    help = 'Imports PTT address data from JSON file'

    def handle(self, *args, **options):
        json_file_path = os.path.join(settings.BASE_DIR, 'addresses', 'ptt_data.json')
        
        if not os.path.exists(json_file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {json_file_path}'))
            return

        self.stdout.write('Loading JSON data...')
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        total_cities = len(data)
        self.stdout.write(f'Found {total_cities} cities. Starting import...')

        with transaction.atomic():
            for city_data in data:
                city_name = city_data['name'].strip()
                # self.stdout.write(f'Processing City: {city_name}')
                
                # Case-insensitive lookup
                city = City.objects.filter(name__iexact=city_name).first()
                
                if not city:
                    # Check by slug to avoid uniqueness error
                    slug = slugify(city_name)
                    city = City.objects.filter(slug=slug).first()
                    
                    if city:
                        # self.stdout.write(f'Found City by slug: {city.name}')
                        pass
                    else:
                        city = City.objects.create(name=city_name)
                        self.stdout.write(f'Created City: {city_name}')
                
                districts_data = city_data.get('districts', [])
                for district_data in districts_data:
                    district_name = district_data['name'].strip()
                    # Case-insensitive lookup within city
                    district = District.objects.filter(city=city, name__iexact=district_name).first()
                    if not district:
                        # Check by slug? District slug is not unique globally, but unique_together=['city', 'name'].
                        # If we have "Merkez" and "MERKEZ", slug is same.
                        # But we want to avoid duplicate names.
                        # If name__iexact failed, it means name is different.
                        # So we can create it.
                        district = District.objects.create(city=city, name=district_name)
                    
                    neighborhoods_data = district_data.get('neighborhoods', [])
                    
                    for neighborhood_data in neighborhoods_data:
                        raw_name = neighborhood_data['name']
                        # Parse neighborhood name: "AKÖREN MAH / MADENLİ / 01722" -> "AKÖREN MAH"
                        neighborhood_name = raw_name.split(' / ')[0].strip()
                        
                        # Case-insensitive lookup within district
                        if not Neighborhood.objects.filter(district=district, name__iexact=neighborhood_name).exists():
                            Neighborhood.objects.create(district=district, name=neighborhood_name)
                
                self.stdout.write(self.style.SUCCESS(f'Processed {city_name}'))

        self.stdout.write(self.style.SUCCESS('Successfully imported all address data'))
