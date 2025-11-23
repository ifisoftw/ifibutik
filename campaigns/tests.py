from django.test import TestCase, Client
from django.urls import reverse
from .models import Campaign, CampaignProduct
from products.models import Product
from addresses.models import City

class CampaignModelTest(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(
            title="Summer Sale",
            slug="summer-sale",
            price=100.00,
            min_quantity=3
        )

    def test_campaign_creation(self):
        """Test campaign creation"""
        self.assertEqual(self.campaign.title, "Summer Sale")
        self.assertEqual(self.campaign.slug, "summer-sale")
        self.assertTrue(self.campaign.is_active)

    def test_slug_uniqueness(self):
        """Test slug uniqueness"""
        with self.assertRaises(Exception):
            Campaign.objects.create(
                title="Another Sale",
                slug="summer-sale", # Duplicate slug
                price=50.00
            )

class CampaignProductModelTest(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(
            title="Winter Sale",
            slug="winter-sale",
            price=200.00
        )
        self.product1 = Product.objects.create(name="P1", sku="S1", stock_qty=10)
        self.product2 = Product.objects.create(name="P2", sku="S2", stock_qty=10)
        
        self.cp1 = CampaignProduct.objects.create(
            campaign=self.campaign,
            product=self.product1,
            sort_order=2
        )
        self.cp2 = CampaignProduct.objects.create(
            campaign=self.campaign,
            product=self.product2,
            sort_order=1
        )

    def test_product_ordering(self):
        """Test that products are ordered by sort_order"""
        products = list(self.campaign.campaignproduct_set.all())
        self.assertEqual(products[0], self.cp2) # sort_order=1
        self.assertEqual(products[1], self.cp1) # sort_order=2

class CampaignViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.campaign = Campaign.objects.create(
            title="Active Campaign",
            slug="active-campaign",
            price=150.00,
            is_active=True
        )
        self.inactive_campaign = Campaign.objects.create(
            title="Inactive Campaign",
            slug="inactive-campaign",
            price=100.00,
            is_active=False
        )
        self.city = City.objects.create(name="Istanbul", slug="istanbul")

    def test_campaign_detail_active(self):
        """Test that active campaign page loads correctly"""
        url = reverse('campaign_detail', args=[self.campaign.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "150₺")
        self.assertIn('products', response.context)
        self.assertIn('cities', response.context)

    def test_campaign_detail_inactive(self):
        """Test that inactive campaign returns 404"""
        url = reverse('campaign_detail', args=[self.inactive_campaign.slug])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)
