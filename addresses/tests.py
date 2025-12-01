from django.test import TestCase
from .models import City, District, Neighborhood

class AddressModelTests(TestCase):
    def test_city_slug_turkish_characters(self):
        """Test that City slug handles Turkish characters correctly."""
        city = City.objects.create(name="İstanbul")
        self.assertEqual(city.slug, "istanbul")
        
        city2 = City.objects.create(name="Iğdır")
        self.assertEqual(city2.slug, "igdir")
        
        city3 = City.objects.create(name="Şanlıurfa")
        self.assertEqual(city3.slug, "sanliurfa")

    def test_district_slug_turkish_characters(self):
        """Test that District slug handles Turkish characters correctly."""
        city = City.objects.create(name="Test City")
        district = District.objects.create(city=city, name="Beşiktaş")
        self.assertEqual(district.slug, "besiktas")
        
        district2 = District.objects.create(city=city, name="Çankaya")
        self.assertEqual(district2.slug, "cankaya")

    def test_neighborhood_slug_turkish_characters(self):
        """Test that Neighborhood slug handles Turkish characters correctly."""
        city = City.objects.create(name="Test City 2")
        district = District.objects.create(city=city, name="Test District")
        neighborhood = Neighborhood.objects.create(district=district, name="Gümüşsuyu")
        self.assertEqual(neighborhood.slug, "gumussuyu")
