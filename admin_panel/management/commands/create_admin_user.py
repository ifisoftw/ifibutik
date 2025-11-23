from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from admin_panel.models import AdminRole, AdminPermission, AdminUser


class Command(BaseCommand):
    help = 'Create admin user with super_admin role'
    
    def handle(self, *args, **kwargs):
        # Create or get super_admin role
        super_admin_role, created = AdminRole.objects.get_or_create(
            name='super_admin',
            defaults={'description': 'Full access to all features'}
        )
        
        if created:
            # Add all permissions to super_admin
            permissions = [
                'view_dashboard',
                'manage_campaigns',
                'manage_products',
                'manage_orders',
                'view_reports',
                'export_data',
                'manage_users',
                'manage_settings',
            ]
            
            for perm in permissions:
                AdminPermission.objects.get_or_create(
                    role=super_admin_role,
                    permission=perm
                )
            
            self.stdout.write(self.style.SUCCESS('Super admin role created with all permissions'))
        
        # Create user
        username = 'admin'
        password = 'admin123'
        
        user, user_created = User.objects.get_or_create(
            username=username,
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True,
            }
        )
        
        if user_created:
            user.set_password(password)
            user.save()
            self.stdout.write(self.style.SUCCESS(f'User created: {username}'))
        
        # Create admin profile
        admin_profile, profile_created = AdminUser.objects.get_or_create(
            user=user,
            defaults={
                'role': super_admin_role,
                'is_active': True
            }
        )
        
        if profile_created:
            self.stdout.write(self.style.SUCCESS('Admin profile created'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Admin User Ready ==='))
        self.stdout.write(f'Username: {username}')
        self.stdout.write(f'Password: {password}')
        self.stdout.write(f'URL: http://localhost:8000/panel/login/')

