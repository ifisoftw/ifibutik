from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import AdminRole, AdminPermission, AdminUser
from django.core.cache import cache
from gumbuz_shop.middleware import get_active_user_count
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import SiteSettings

class AdminLoginTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.role = AdminRole.objects.create(name='admin', description='Admin Role')
        self.admin_user = AdminUser.objects.create(user=self.user, role=self.role)
        AdminPermission.objects.create(role=self.role, permission='view_dashboard')
        
        # Give permission to view dashboard (needed for redirect check if login succeeds and redirects to dashboard)
        # Actually login view redirects to dashboard if successful.
        # Dashboard view checks permission.
        # But login view itself just checks if user has admin_profile.
        
    def test_login_page_loads(self):
        """Test login page loads"""
        url = reverse('admin_login')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Giriş Yap")

    def test_valid_login(self):
        """Test valid login redirects to dashboard"""
        url = reverse('admin_login')
        data = {'username': 'admin', 'password': 'password'}
        response = self.client.post(url, data)
        self.assertRedirects(response, reverse('admin_dashboard'))

    def test_invalid_login(self):
        """Test invalid login returns error"""
        url = reverse('admin_login')
        data = {'username': 'admin', 'password': 'wrongpassword'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kullanıcı adı veya şifre hatalı")

class AdminDashboardTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.role = AdminRole.objects.create(name='admin', description='Admin Role')
        self.admin_user = AdminUser.objects.create(user=self.user, role=self.role)
        
        self.permission = AdminPermission.objects.create(
            role=self.role,
            permission='view_dashboard'
        )

    def test_dashboard_access_denied_anonymous(self):
        """Test dashboard requires login"""
        url = reverse('admin_dashboard')
        response = self.client.get(url)
        self.assertRedirects(response, reverse('admin_login'))

    def test_dashboard_access_denied_no_permission(self):
        """Test dashboard requires permission"""
        # Remove permission
        self.permission.delete()
        self.client.login(username='admin', password='password')
        
        url = reverse('admin_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    def test_dashboard_access_granted(self):
        """Test dashboard accessible with permission"""
        self.client.login(username='admin', password='password')
        url = reverse('admin_dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)



class ActiveUserTrackingTest(TestCase):
    def setUp(self):
        self.client = Client()
        # Clear cache before each test
        cache.delete('active_users_dict')

    def test_active_user_count_increases(self):
        """Test that a request increases the active user count"""
        # Initial count should be 0
        self.assertEqual(get_active_user_count(), 0)
        
        # Make a request (this should trigger middleware)
        # We need to ensure session is created/accessed
        session = self.client.session
        session['test'] = 'true'
        session.save()
        
        self.client.get(reverse('admin_login'))
        
        # Count should be 1
        self.assertEqual(get_active_user_count(), 1)

    def test_active_user_count_multiple_users(self):
        """Test that multiple distinct sessions are counted separately"""
        # User 1
        client1 = Client()
        session1 = client1.session
        session1['user'] = '1'
        session1.save()
        client1.get(reverse('admin_login'))
        
        # User 2
        client2 = Client()
        session2 = client2.session
        session2['user'] = '2'
        session2.save()
        client2.get(reverse('admin_login'))
        
        self.assertEqual(get_active_user_count(), 2)

    def test_context_processor(self):
        """Test that the context processor adds the count to the template context"""
        # Make a request
        session = self.client.session
        session['test'] = 'true'
        session.save()
        
        response = self.client.get(reverse('admin_login'))
        
        # Check context
        self.assertIn('active_user_count', response.context)
        self.assertEqual(response.context['active_user_count'], 1)

        self.assertEqual(response.context['active_user_count'], 1)

class AdminSettingsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='admin', password='password')
        self.role = AdminRole.objects.create(name='admin', description='Admin Role')
        self.admin_user = AdminUser.objects.create(user=self.user, role=self.role)
        # Give permission to manage settings
        AdminPermission.objects.create(role=self.role, permission='manage_settings')
        self.client.login(username='admin', password='password')

    def test_settings_save(self):
        """Test saving settings"""
        url = reverse('admin_settings')
        data = {
            'store_name': 'New Store Name',
            'rate_limit_count': 10,
            'rate_limit_period': 300
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, url)
        
        settings = SiteSettings.load()
        self.assertEqual(settings.store_name, 'New Store Name')
        self.assertEqual(settings.rate_limit_count, 10)
        self.assertEqual(settings.rate_limit_period, 300)

    def test_settings_invalid_rate_limits(self):
        """Test that negative rate limits are rejected"""
        url = reverse('admin_settings')
        data = {
            'rate_limit_count': -5,
            'rate_limit_period': -100
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, url)
        
        # Check messages
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("pozitif olmalı" in str(m) for m in messages))
        
        # Verify settings NOT changed (should keep defaults or previous values)
        settings = SiteSettings.load()
        self.assertNotEqual(settings.rate_limit_count, -5)
        self.assertNotEqual(settings.rate_limit_period, -100)

    def test_file_upload_validation_extension(self):
        """Test file upload validation for invalid extension"""
        url = reverse('admin_settings')
        
        # Create a fake text file
        file_content = b"fake image content"
        uploaded_file = SimpleUploadedFile("test.txt", file_content, content_type="text/plain")
        
        data = {
            'store_logo': uploaded_file
        }
        response = self.client.post(url, data)
        
        # Should redirect back with error
        self.assertRedirects(response, url)
        
        # Check messages (need to follow redirect or check response cookies/storage)
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("Sadece JPG ve PNG" in str(m) for m in messages))

    def test_fake_image_content(self):
        """Test that a file with valid extension but invalid content is rejected"""
        url = reverse('admin_settings')
        
        # Create a text file renamed to .jpg
        file_content = b"This is not an image"
        uploaded_file = SimpleUploadedFile("fake.jpg", file_content, content_type="image/jpeg")
        
        data = {
            'store_logo': uploaded_file
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, url)
        
        # We expect this to fail validation if we implement content checking.
        # Currently, it might pass if we only check extension.
        # Let's see if it passes or fails.
        # If it passes (file saved), then we have a vulnerability to fix.
        
        # For now, let's assert that it SHOULD fail (message contains error)
        # If this assertion fails, we know we need to fix the view.
        messages = list(response.wsgi_request._messages)
        
        # If strict validation is missing, this test will fail (because no error message).
        # We will use this failure to drive the fix.
        self.assertTrue(any("Geçersiz resim dosyası" in str(m) or "Hata" in str(m) for m in messages))

    def test_file_upload_validation_size(self):
        """Test file upload validation for large size"""
        url = reverse('admin_settings')
        
        # Create a large fake image (3MB)
        file_content = b"x" * (3 * 1024 * 1024)
        uploaded_file = SimpleUploadedFile("large.png", file_content, content_type="image/png")
        
        data = {
            'store_logo': uploaded_file
        }
        response = self.client.post(url, data)
        
        messages = list(response.wsgi_request._messages)
        self.assertTrue(any("2MB'dan büyük olamaz" in str(m) for m in messages))

    def test_file_upload_success(self):
        """Test successful file upload"""
        url = reverse('admin_settings')
        
        # Create a valid small image (1x1 PNG)
        # Minimal PNG signature and IHDR
        file_content = (
            b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a'  # Signature
            b'\x00\x00\x00\x0d\x49\x48\x44\x52'  # IHDR
            b'\x00\x00\x00\x01\x00\x00\x00\x01'  # Width/Height
            b'\x08\x06\x00\x00\x00\x1f\x15\xc4'  # Bit depth/Color type
            b'\x89\x00\x00\x00\x0a\x49\x44\x41'  # IDAT
            b'\x54\x78\x9c\x63\x00\x01\x00\x00'  # Data
            b'\x05\x00\x01\x0d\x0a\x2d\xb4\x00'  # Data
            b'\x00\x00\x00\x49\x45\x4e\x44\xae'  # IEND
            b'\x42\x60\x82'
        )
        uploaded_file = SimpleUploadedFile("logo.png", file_content, content_type="image/png")
        
        data = {
            'store_logo': uploaded_file
        }
        response = self.client.post(url, data)
        self.assertRedirects(response, url)
        
        settings = SiteSettings.load()
        self.assertTrue(settings.store_logo)
        # Check if file exists (name will be changed by Django)
        self.assertTrue(settings.store_logo)
        self.assertTrue(settings.store_logo.name.startswith('settings/logo'))

    def test_settings_save_permission_required(self):
        """Test that saving settings requires permission"""
        # Remove permission
        self.admin_user.role.permissions.all().delete()
        
        url = reverse('admin_settings')
        data = {
            'store_name': 'Hacked Store Name'
        }
        response = self.client.post(url, data)
        
        # Should be forbidden (403)
        self.assertEqual(response.status_code, 403)
        
        # Verify settings NOT changed
        settings = SiteSettings.load()
        self.assertNotEqual(settings.store_name, 'Hacked Store Name')
