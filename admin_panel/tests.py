from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import AdminRole, AdminPermission, AdminUser
from django.core.cache import cache
from gumbuz_shop.middleware import get_active_user_count

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

