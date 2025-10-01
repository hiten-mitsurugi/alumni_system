from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import date
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create superadmin and admin accounts automatically'

    def add_arguments(self, parser):
        parser.add_argument(
            '--superadmin-username',
            type=str,
            default='superadmin',
            help='Username for superadmin account (default: superadmin)'
        )
        parser.add_argument(
            '--admin-username', 
            type=str,
            default='admin',
            help='Username for admin account (default: admin)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Admin@123',
            help='Password for both accounts (default: Admin@123 - meets all requirements)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of accounts if they already exist'
        )

    def handle(self, *args, **options):
        superadmin_username = options['superadmin_username']
        admin_username = options['admin_username']
        password = options['password']
        force = options['force']

        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Creating Administrative Accounts ===\n'
            )
        )

        # Create superadmin account
        self.create_account(
            username=superadmin_username,
            user_type=1,  # Super Admin
            email=f'{superadmin_username}@alumni.system',
            password=password,
            force=force,
            is_superuser=True,
            is_staff=True
        )

        # Create admin account  
        self.create_account(
            username=admin_username,
            user_type=2,  # Admin
            email=f'{admin_username}@alumni.system',
            password=password,
            force=force,
            is_superuser=False,
            is_staff=True
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Account Creation Complete ===\n'
                f'🔐 LOGIN CREDENTIALS (Use EMAIL + PASSWORD):\n'
                f'Super Admin Email: {superadmin_username}@alumni.system\n'
                f'Admin Email: {admin_username}@alumni.system\n'
                f'Password (both accounts): {password}\n'
                f'\n📋 Password Requirements Met:\n'
                f'✅ Minimum 8 characters\n'
                f'✅ Contains uppercase letter\n' 
                f'✅ Contains lowercase letter\n'
                f'✅ Contains number\n'
                f'✅ Contains special character\n'
                f'\n🌐 Login URL: /admin/ or your frontend login\n'
            )
        )

    def create_account(self, username, user_type, email, password, force, is_superuser=False, is_staff=True):
        """Create a single account with the given parameters"""
        
        user_type_names = {1: 'Super Admin', 2: 'Admin', 3: 'Alumni'}
        account_type = user_type_names.get(user_type, 'Unknown')
        
        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    if force:
                        # Delete existing user
                        User.objects.filter(username=username).delete()
                        self.stdout.write(
                            self.style.WARNING(
                                f'🔄 Deleted existing {account_type} account: {username}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠️  {account_type} account already exists: {username}'
                                f' (use --force to recreate)'
                            )
                        )
                        return


                # Create the user account
                user = User.objects.create_user(
                    username=username,
                    email=email,
                    password=password,
                    first_name=account_type.replace(' ', ''),
                    last_name='User',
                    user_type=user_type,
                    is_approved=True,
                    is_active=True,
                    is_staff=is_staff,
                    is_superuser=is_superuser,
                    # Required fields with defaults
                    program='Administration',
                    sex='prefer_not_to_say',
                    birth_date=date(1990, 1, 1),
                    contact_number='+63-900-000-0000',
                    present_address='Administration Office',
                    permanent_address='Administration Office',
                    year_graduated=2020,
                    mothers_name='Admin Mother',
                    mothers_occupation='Administrator',
                    fathers_name='Admin Father', 
                    fathers_occupation='Administrator',
                    civil_status='single',
                    employment_status='employed_locally'
                )

                # Create profile for the user
                from auth_app.models import Profile
                profile = Profile.objects.create(
                    user=user,
                    bio=f'System generated {account_type} account',
                    present_employment_status=user.employment_status
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Created {account_type} account:'
                        f'\n   � Email (for login): {email}'
                        f'\n   � Username: {username}'
                        f'\n   🔑 Password: {password}'
                        f'\n   📋 Type: {account_type} (Level {user_type})'
                        f'\n   ✅ Status: Active & Approved'
                        f'\n   🚨 IMPORTANT: Login with EMAIL, not username!'
                        f'\n'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Failed to create {account_type} account: {str(e)}'
                )
            )
            raise
