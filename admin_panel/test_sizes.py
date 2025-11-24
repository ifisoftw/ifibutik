from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from campaigns.models import SizeOption, Campaign
from admin_panel.models import AdminRole, AdminPermission, AdminUser


class SizeOptionModelTest(TestCase):
    """Test cases for SizeOption model"""
    
    def setUp(self):
        self.size = SizeOption.objects.create(
            name="Large",
            slug="large",
            description="Large size",
            is_active=True
        )
    
    def test_size_creation(self):
        """Test size option creation"""
        self.assertEqual(self.size.name, "Large")
        self.assertEqual(self.size.slug, "large")
        self.assertEqual(self.size.description, "Large size")
        self.assertTrue(self.size.is_active)
    
    def test_size_string_representation(self):
        """Test __str__ method"""
        self.assertEqual(str(self.size), "Large")
    
    def test_slug_uniqueness(self):
        """Test slug uniqueness constraint"""
        with self.assertRaises(Exception):
            SizeOption.objects.create(
                name="Another Large",
                slug="large",  # Duplicate slug
                description="Another large size"
            )
    
    def test_size_defaults(self):
        """Test default values"""
        size = SizeOption.objects.create(name="Medium", slug="medium")
        self.assertTrue(size.is_active)  # Default should be True
        self.assertEqual(size.description, "")  # Default should be empty


class SizeManagementViewTest(TestCase):
    """Test cases for size management views"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user with permissions
        self.user = User.objects.create_user(username='admin', password='password')
        self.role = AdminRole.objects.create(name='admin', description='Admin Role')
        self.admin_user = AdminUser.objects.create(user=self.user, role=self.role)
        
        # Add manage_products permission (required for size management)
        AdminPermission.objects.create(role=self.role, permission='manage_products')
        
        # Create test sizes
        self.size1 = SizeOption.objects.create(
            name="Small",
            slug="small",
            description="Small size",
            is_active=True
        )
        self.size2 = SizeOption.objects.create(
            name="Medium",
            slug="medium",
            description="Medium size",
            is_active=True
        )
        self.size3 = SizeOption.objects.create(
            name="Large",
            slug="large",
            description="Large size",
            is_active=False
        )
        
        # Login
        self.client.login(username='admin', password='password')
    
    def test_size_list_access(self):
        """Test size list page loads correctly"""
        url = reverse('admin_sizes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Small")
        self.assertContains(response, "Medium")
        self.assertContains(response, "Large")
    
    def test_size_list_requires_login(self):
        """Test size list requires authentication"""
        self.client.logout()
        url = reverse('admin_sizes')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('admin_login'))
    
    def test_size_list_statistics(self):
        """Test statistics in size list"""
        url = reverse('admin_sizes')
        response = self.client.get(url)
        self.assertEqual(response.context['stats']['total'], 3)
        self.assertEqual(response.context['stats']['active'], 2)
        self.assertEqual(response.context['stats']['inactive'], 1)
    
    def test_size_list_search(self):
        """Test search functionality"""
        url = reverse('admin_sizes') + '?search=small'
        response = self.client.get(url)
        self.assertContains(response, "Small")
        self.assertNotContains(response, "Medium")
    
    def test_size_list_status_filter(self):
        """Test status filter"""
        # Filter active
        url = reverse('admin_sizes') + '?status=active'
        response = self.client.get(url)
        self.assertEqual(len(response.context['page_obj']), 2)
        
        # Filter inactive
        url = reverse('admin_sizes') + '?status=inactive'
        response = self.client.get(url)
        self.assertEqual(len(response.context['page_obj']), 1)
    
    def test_size_list_sorting(self):
        """Test sorting functionality"""
        url = reverse('admin_sizes') + '?sort=name&dir=asc'
        response = self.client.get(url)
        sizes = list(response.context['page_obj'])
        self.assertEqual(sizes[0].name, "Large")
        self.assertEqual(sizes[1].name, "Medium")
        self.assertEqual(sizes[2].name, "Small")
    
    def test_size_create_modal_get(self):
        """Test size create modal loads"""
        url = reverse('admin_size_create')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Yeni Beden Ekle")
    
    def test_size_create_modal_post_success(self):
        """Test successful size creation"""
        url = reverse('admin_size_create')
        data = {
            'name': 'Extra Large',
            'slug': 'xl',
            'description': 'XL size',
            'is_active': 'on'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # Verify size was created
        size = SizeOption.objects.get(slug='xl')
        self.assertEqual(size.name, 'Extra Large')
        self.assertEqual(size.description, 'XL size')
        self.assertTrue(size.is_active)
    
    def test_size_create_auto_slug(self):
        """Test automatic slug generation"""
        url = reverse('admin_size_create')
        data = {
            'name': 'Extra Small',
            'slug': '',  # Empty slug
            'is_active': 'on'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # Verify size was created with auto-generated slug
        size = SizeOption.objects.get(name='Extra Small')
        self.assertEqual(size.slug, 'extra-small')
    
    def test_size_create_duplicate_slug(self):
        """Test duplicate slug validation"""
        url = reverse('admin_size_create')
        data = {
            'name': 'Another Small',
            'slug': 'small',  # Duplicate
            'is_active': 'on'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Bu slug (kod) zaten kullanımda', status_code=400)
    
    def test_size_edit_modal_get(self):
        """Test size edit modal loads"""
        url = reverse('admin_size_edit', args=[self.size1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Beden Düzenle")
        self.assertContains(response, self.size1.name)
    
    def test_size_update_success(self):
        """Test successful size update"""
        url = reverse('admin_size_update', args=[self.size1.id])
        data = {
            'name': 'Extra Small',
            'slug': 'xs',
            'description': 'Updated description',
            'is_active': ''  # Unchecked
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # Verify update
        self.size1.refresh_from_db()
        self.assertEqual(self.size1.name, 'Extra Small')
        self.assertEqual(self.size1.slug, 'xs')
        self.assertEqual(self.size1.description, 'Updated description')
        self.assertFalse(self.size1.is_active)
    
    def test_size_update_duplicate_slug(self):
        """Test update with duplicate slug validation"""
        url = reverse('admin_size_update', args=[self.size1.id])
        data = {
            'name': 'Small',
            'slug': 'medium',  # Duplicate of size2
            'is_active': 'on'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
    
    def test_size_delete(self):
        """Test size deletion"""
        url = reverse('admin_size_delete', args=[self.size1.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        self.assertFalse(SizeOption.objects.filter(id=self.size1.id).exists())
    
    def test_size_toggle(self):
        """Test size toggle functionality"""
        url = reverse('admin_size_toggle', args=[self.size1.id])
        
        # Toggle from active to inactive
        initial_status = self.size1.is_active
        response = self.client.post(url)
        self.assertEqual(response.status_code, 200)
        
        self.size1.refresh_from_db()
        self.assertNotEqual(self.size1.is_active, initial_status)
        
        # Toggle back
        response = self.client.post(url)
        self.size1.refresh_from_db()
        self.assertEqual(self.size1.is_active, initial_status)
    
    def test_size_bulk_activate(self):
        """Test bulk activate action"""
        url = reverse('admin_size_bulk_action')
        data = {
            'action': 'activate',
            'selected_items': [self.size3.id]  # Inactive size
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        self.size3.refresh_from_db()
        self.assertTrue(self.size3.is_active)
    
    def test_size_bulk_deactivate(self):
        """Test bulk deactivate action"""
        url = reverse('admin_size_bulk_action')
        data = {
            'action': 'deactivate',
            'selected_items': [self.size1.id, self.size2.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        self.size1.refresh_from_db()
        self.size2.refresh_from_db()
        self.assertFalse(self.size1.is_active)
        self.assertFalse(self.size2.is_active)
    
    def test_size_bulk_delete(self):
        """Test bulk delete action"""
        url = reverse('admin_size_bulk_action')
        data = {
            'action': 'delete',
            'selected_items': [self.size1.id, self.size2.id]
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        self.assertFalse(SizeOption.objects.filter(id=self.size1.id).exists())
        self.assertFalse(SizeOption.objects.filter(id=self.size2.id).exists())
        self.assertTrue(SizeOption.objects.filter(id=self.size3.id).exists())
    
    def test_size_bulk_action_no_selection(self):
        """Test bulk action with no items selected"""
        url = reverse('admin_size_bulk_action')
        data = {
            'action': 'activate',
            'selected_items': []
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)


class SizeQuickCreateTest(TestCase):
    """Test cases for inline size creation from campaign modal"""
    
    def setUp(self):
        self.client = Client()
        
        # Create admin user with permissions
        self.user = User.objects.create_user(username='admin', password='password')
        self.role = AdminRole.objects.create(name='admin', description='Admin Role')
        self.admin_user = AdminUser.objects.create(user=self.user, role=self.role)
        AdminPermission.objects.create(role=self.role, permission='manage_products')
        
        # Create campaign
        self.campaign = Campaign.objects.create(
            title="Test Campaign",
            slug="test-campaign",
            price=100.00
        )
        
        # Create existing sizes
        self.size1 = SizeOption.objects.create(
            name="Small",
            slug="small",
            is_active=True
        )
        
        # Login
        self.client.login(username='admin', password='password')
    
    def test_quick_create_new_size(self):
        """Test quick create creates a new size"""
        url = reverse('admin_size_quick_create')
        data = {
            'name': 'Medium',
            'description': 'M size',
            'campaign_id': self.campaign.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # Verify size was created
        size = SizeOption.objects.get(slug='medium')
        self.assertEqual(size.name, 'Medium')
        self.assertEqual(size.description, 'M size')
        self.assertTrue(size.is_active)
    
    def test_quick_create_existing_size(self):
        """Test quick create with existing slug returns existing size"""
        url = reverse('admin_size_quick_create')
        data = {
            'name': 'Small',  # Already exists
            'description': '',
            'campaign_id': self.campaign.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # Should not create duplicate
        self.assertEqual(SizeOption.objects.filter(slug='small').count(), 1)
    
    def test_quick_create_empty_name(self):
        """Test quick create with empty name"""
        url = reverse('admin_size_quick_create')
        data = {
            'name': '',
            'campaign_id': self.campaign.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 400)
        self.assertContains(response, 'Beden ismi gerekli', status_code=400)
    
    def test_quick_create_returns_checkboxes(self):
        """Test quick create returns updated checkbox list"""
        url = reverse('admin_size_quick_create')
        data = {
            'name': 'Large',
            'campaign_id': self.campaign.id
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        
        # Should contain the new size in response
        self.assertContains(response, 'Large')
        # Should also contain existing sizes
        self.assertContains(response, 'Small')
