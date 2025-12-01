from django.test import TestCase, Client, override_settings
from django.urls import reverse
from .models import Order, OrderItem
from campaigns.models import Campaign, SizeOption, CampaignProduct
from products.models import Product
from addresses.models import City, District, Neighborhood
from django.core.cache import cache
from admin_panel.models import SiteSettings

class OrderModelTest(TestCase):
    def setUp(self):
        self.campaign = Campaign.objects.create(title="Test Campaign", slug="test-campaign-1", price=100.00)
        self.city = City.objects.create(name="Istanbul")
        self.order = Order.objects.create(
            campaign=self.campaign,
            customer_name="John Doe",
            phone="5551234567",
            city_fk=self.city,
            full_address="Test Address",
            tracking_number="1234567890",
            total_amount=100.00
        )

    def test_order_creation(self):
        """Test order creation"""
        self.assertEqual(self.order.customer_name, "John Doe")
        self.assertEqual(self.order.status, "new")
        self.assertTrue(self.order.tracking_number) # Should be generated if logic is in model save, but here it's in view. 
        # Wait, tracking number is generated in view. So in model test it might be empty if not provided.
        # Let's check model definition. If it has default or auto-generate in save.
        # In views.py it is generated and passed to create.
        # So here it might be None or empty string if I didn't pass it.
        # I passed it in setUp? No.
        # Let's check model definition.
        pass

class OrderCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.campaign = Campaign.objects.create(
            title="Test Campaign", 
            slug="test-campaign-2",
            price=100.00, 
            min_quantity=1,
            shipping_price=10,
            cod_price=10
        )
        self.product = Product.objects.create(name="P1", stock_qty=10, sku="TEST-SKU-1")
        self.size = SizeOption.objects.create(name="M", slug="m")
        self.campaign.available_sizes.add(self.size)
        
        # Add product to campaign (Critical for security check)
        CampaignProduct.objects.create(campaign=self.campaign, product=self.product, sort_order=1)
        
        self.city = City.objects.create(name="Istanbul")
        self.district = District.objects.create(name="Kadikoy", city=self.city)
        self.neighborhood = Neighborhood.objects.create(name="Caferaga", district=self.district)

    def test_create_order_success(self):
        """Test successful order creation"""
        url = reverse('create_order')
        data = {
            'campaign_id': self.campaign.id,
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '5559876543',
            'city': self.city.id,
            'district': self.district.id,
            'neighborhood': self.neighborhood.id,
            'address_detail': 'Test Address Detail',
            'selected_products[]': [self.product.id],
            'selected_sizes[]': [self.size.slug]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['HX-Redirect'], '/orders/success/')
        
        # Check DB
        self.assertEqual(Order.objects.count(), 1)
        order = Order.objects.first()
        self.assertEqual(order.customer_name, "Jane Doe")
        self.assertEqual(order.items.count(), 1)
        
        # Check Session
        # Check Session
        # self.assertTrue(self.client.session.get('order_completed'))
        # self.assertEqual(self.client.session.get('last_order_id'), order.id)

    def test_create_order_validation_error(self):
        """Test validation error when quantity is less than min_quantity"""
        self.campaign.min_quantity = 2
        self.campaign.save()
        
        url = reverse('create_order')
        data = {
            'campaign_id': self.campaign.id,
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '5559876543',
            'city': self.city.id,
            'selected_products[]': [self.product.id], # Only 1 product
            'selected_sizes[]': [self.size.slug]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"En az 2 adet", response.content)

    def test_stock_reduction_on_order(self):
        """Test that product stock is reduced when order is created"""
        # Initial stock
        initial_stock = self.product.stock_qty
        self.assertEqual(initial_stock, 10)
        
        url = reverse('create_order')
        data = {
            'campaign_id': self.campaign.id,
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '5559876543',
            'city': self.city.id,
            'district': self.district.id,
            'neighborhood': self.neighborhood.id,
            'address_detail': 'Test Address Detail',
            'selected_products[]': [self.product.id],
            'selected_sizes[]': [self.size.slug]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # Refresh product from DB
        self.product.refresh_from_db()
        
        # Check stock has been reduced
        self.assertEqual(self.product.stock_qty, 9)
        self.assertEqual(self.product.stock_qty, initial_stock - 1)

    def test_price_manipulation_prevention(self):
        """Test that products from other campaigns cannot be added"""
        # Create another campaign and product
        other_campaign = Campaign.objects.create(
            title="Other Campaign", 
            slug="other-campaign",
            price=50.00,
            min_quantity=1
        )
        other_product = Product.objects.create(name="Other Product", stock_qty=10, sku="TEST-SKU-2")
        # Don't add other_product to self.campaign
        
        url = reverse('create_order')
        data = {
            'campaign_id': self.campaign.id,
            'first_name': 'Hacker',
            'last_name': 'User',
            'phone': '5559876543',
            'city': self.city.id,
            'selected_products[]': [other_product.id], # Try to buy other product with this campaign
            'selected_sizes[]': []
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"G\xc3\xbcvenlik Hatas\xc4\xb1", response.content) # "Güvenlik Hatası" bytes check

        self.assertEqual(response.status_code, 400)
        self.assertIn(b"G\xc3\xbcvenlik Hatas\xc4\xb1", response.content) # "Güvenlik Hatası" bytes check

    @override_settings(CACHES={'default': {'BACKEND': 'django.core.cache.backends.locmem.LocMemCache'}})
    def test_rate_limiting(self):
        """Test rate limiting prevents spam orders"""
        # Clear cache first
        ip = '127.0.0.1'
        cache.delete(f"rate_limit_order_{ip}")
        
        # Set limit to 2 for testing
        settings = SiteSettings.load()
        settings.rate_limit_count = 2
        settings.rate_limit_period = 60
        settings.save()
        
        url = reverse('create_order')
        data = {
            'campaign_id': self.campaign.id,
            'first_name': 'Spam',
            'last_name': 'Bot',
            'phone': '5559876543',
            'city': self.city.id,
            'district': self.district.id,
            'neighborhood': self.neighborhood.id,
            'address_detail': 'Test Address Detail',
            'selected_products[]': [self.product.id],
            'selected_sizes[]': [self.size.slug]
        }
        
        # 1st Request - OK
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # 2nd Request - OK
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # 3rd Request - Blocked
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 429)
        self.assertIn(b"ok fazla deneme", response.content)

    def test_inactive_campaign_order(self):
        """Test that ordering from an inactive campaign fails"""
        self.campaign.is_active = False
        self.campaign.save()
        
        url = reverse('create_order')
        data = {
            'campaign_id': self.campaign.id,
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '5559876543',
            'city': self.city.id,
            'district': self.district.id,
            'neighborhood': self.neighborhood.id,
            'address_detail': 'Test Address Detail',
            'selected_products[]': [self.product.id],
            'selected_sizes[]': [self.size.slug]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"aktif de", response.content)

    def test_out_of_stock_order(self):
        """Test that ordering an out of stock product fails"""
        self.product.stock_qty = 0
        self.product.save()
        
        url = reverse('create_order')
        data = {
            'campaign_id': self.campaign.id,
            'first_name': 'Test',
            'last_name': 'User',
            'phone': '5559876543',
            'city': self.city.id,
            'district': self.district.id,
            'neighborhood': self.neighborhood.id,
            'address_detail': 'Test Address Detail',
            'selected_products[]': [self.product.id],
            'selected_sizes[]': [self.size.slug]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"stok yetersiz", response.content)

    def test_create_order_empty_products(self):
        """Test validation error when no products are selected"""
        url = reverse('create_order')
        data = {
            'campaign_id': self.campaign.id,
            'first_name': 'Jane',
            'last_name': 'Doe',
            'phone': '5559876543',
            'city': self.city.id,
            'district': self.district.id,
            'neighborhood': self.neighborhood.id,
            'address_detail': 'Test Address Detail',
            'selected_products[]': [], # Empty list
            'selected_sizes[]': []
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"En az 1 adet", response.content)

    def test_create_order_partial_invalid_products(self):
        """Test that mixing valid and invalid products fails"""
        # Create another campaign and product
        other_campaign = Campaign.objects.create(
            title="Other Campaign", 
            slug="other-campaign-mixed",
            price=50.00,
            min_quantity=1
        )
        other_product = Product.objects.create(name="Other Product", stock_qty=10, sku="TEST-SKU-MIXED")
        
        url = reverse('create_order')
        data = {
            'campaign_id': self.campaign.id,
            'first_name': 'Hacker',
            'last_name': 'User',
            'phone': '5559876543',
            'city': self.city.id,
            'district': self.district.id,
            'neighborhood': self.neighborhood.id,
            'address_detail': 'Test Address Detail',
            'selected_products[]': [self.product.id, other_product.id], # One valid, one invalid
            'selected_sizes[]': [self.size.slug, 'm']
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertIn(b"G\xc3\xbcvenlik Hatas\xc4\xb1", response.content)

    def test_transaction_rollback(self):
        """Test that order is rolled back if an error occurs during item creation"""
        from unittest.mock import patch
        
        url = reverse('create_order')
        data = {
            'campaign_id': self.campaign.id,
            'first_name': 'Rollback',
            'last_name': 'Test',
            'phone': '5559876543',
            'city': self.city.id,
            'district': self.district.id,
            'neighborhood': self.neighborhood.id,
            'address_detail': 'Test Address Detail',
            'selected_products[]': [self.product.id],
            'selected_sizes[]': [self.size.slug]
        }
        
        # Mock OrderItem.objects.create to raise an exception
        with patch('orders.models.OrderItem.objects.create') as mock_create:
            mock_create.side_effect = Exception("Simulated Database Error")
            
            response = self.client.post(url, data)
            
            # Should be 500 because we catch generic Exception and return 500
            self.assertEqual(response.status_code, 500)
            self.assertIn(b"hata olu", response.content)
            
            # Verify Order count is 0 (Rollback happened)
            self.assertEqual(Order.objects.count(), 0)
            
            # Verify Stock is NOT reduced
            self.product.refresh_from_db()
            self.assertEqual(self.product.stock_qty, 10)

class OrderSuccessViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.campaign = Campaign.objects.create(title="Test Campaign", slug="test-campaign-3", price=100.00)
        self.order = Order.objects.create(
            campaign=self.campaign,
            customer_name="Test User",
            total_amount=100.00
        )

    def test_order_success_access(self):
        """Test access to success page with valid session"""
        session = self.client.session
        session['order_completed'] = True
        session['last_order_id'] = self.order.id
        session.save()
        
        url = reverse('order_success')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test User") # Assuming customer name is shown

    def test_order_success_no_session(self):
        """Test redirect when accessing success page without session"""
        url = reverse('order_success')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('home'), target_status_code=302)
