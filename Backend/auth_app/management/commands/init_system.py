from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import date
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Initialize the system with default administrative accounts and sample data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='Admin@123',
            help='Default password for all accounts (default: Admin@123 - meets requirements)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of accounts if they already exist'
        )
        parser.add_argument(
            '--skip-alumni',
            action='store_true',
            help='Skip creating sample alumni accounts'
        )

    def handle(self, *args, **options):
        password = options['password']
        force = options['force']
        skip_alumni = options['skip_alumni']

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎯 === ALUMNI SYSTEM INITIALIZATION ===\n'
            )
        )

        # Create administrative accounts
        self.create_admin_accounts(password, force)
        
        # Create sample alumni accounts (unless skipped)
        if not skip_alumni:
            self.create_sample_alumni(password, force)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎉 === INITIALIZATION COMPLETE ===\n'
                f'🔐 Default Password: {password}\n'
                f'🚨 IMPORTANT: Login with EMAIL addresses, not usernames!\n'
                f'📧 Admin Emails: superadmin@alumni.system, admin@alumni.system\n'
                f'🌐 Access the admin panel at: /admin/\n'
                f'\n� Password meets all requirements:\n'
                f'✅ 8+ characters, uppercase, lowercase, number, special char\n'
            )
        )

    def create_admin_accounts(self, password, force):
        """Create administrative accounts"""
        self.stdout.write(
            self.style.HTTP_INFO('🔧 Creating Administrative Accounts...\n')
        )

        # Define admin accounts to create (only the 2 admin types)
        admin_accounts = [
            {
                'username': 'superadmin',
                'user_type': 1,
                'email': 'superadmin@alumni.system',
                'first_name': 'Super',
                'last_name': 'Administrator',
                'is_superuser': True,
                'is_staff': True,
                'program': 'System Administration'
            },
            {
                'username': 'admin',
                'user_type': 2,
                'email': 'admin@alumni.system', 
                'first_name': 'System',
                'last_name': 'Administrator',
                'is_superuser': False,
                'is_staff': True,
                'program': 'System Administration'
            }
        ]

        for account_data in admin_accounts:
            self.create_account(account_data, password, force)

    def create_sample_alumni(self, password, force):
        """Create sample alumni accounts for testing"""
        self.stdout.write(
            self.style.HTTP_INFO('👥 Creating Sample Alumni Accounts...\n')
        )

        # Sample alumni data (user type 3)
        sample_alumni = [
            {
                'username': 'john.doe',
                'user_type': 3,  # Alumni
                'email': 'john.doe@alumni.system',
                'first_name': 'John',
                'last_name': 'Doe',
                'program': 'Computer Science',
                'year_graduated': 2020,
                'employment_status': 'employed_locally'
            },
            {
                'username': 'jane.smith',
                'user_type': 3,  # Alumni
                'email': 'jane.smith@alumni.system',
                'first_name': 'Jane',
                'last_name': 'Smith', 
                'program': 'Information Technology',
                'year_graduated': 2019,
                'employment_status': 'employed_internationally'
            },
            {
                'username': 'mike.johnson',
                'user_type': 3,  # Alumni
                'email': 'mike.johnson@alumni.system',
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'program': 'Engineering',
                'year_graduated': 2021,
                'employment_status': 'self_employed'
            }
        ]

        for account_data in sample_alumni:
            self.create_account(account_data, password, force)

    def create_account(self, account_data, password, force):
        """Create a single account with the given parameters"""
        
        username = account_data['username']
        user_type = account_data['user_type']
        
        user_type_names = {1: 'Super Admin', 2: 'Admin', 3: 'Alumni'}
        account_type = user_type_names.get(user_type, 'Unknown')
        
        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    if force:
                        User.objects.filter(username=username).delete()
                        self.stdout.write(
                            self.style.WARNING(
                                f'🔄 Deleted existing account: {username}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠️  Account already exists: {username} (use --force to recreate)'
                            )
                        )
                        return

                # Create the user account (school_id removed)
                user = User.objects.create_user(
                    username=username,
                    email=account_data['email'],
                    password=password,
                    first_name=account_data['first_name'],
                    last_name=account_data['last_name'],
                    user_type=user_type,
                    program=account_data['program'],
                    is_approved=True,
                    is_active=True,
                    is_staff=account_data.get('is_staff', user_type <= 2),
                    is_superuser=account_data.get('is_superuser', False),
                    # Default values for required fields
                    sex='prefer_not_to_say',
                    birth_date=date(1995, 1, 1),
                    contact_number=f'+63-9{random.randint(100000000, 999999999)}',
                    present_address='Sample Address',
                    permanent_address='Sample Permanent Address',
                    year_graduated=account_data.get('year_graduated', 2020),
                    mothers_name='Sample Mother',
                    mothers_occupation='Sample Occupation',
                    fathers_name='Sample Father',
                    fathers_occupation='Sample Occupation',
                    civil_status='single',
                    employment_status=account_data.get('employment_status', 'employed_locally')
                )

                # Create profile
                from auth_app.models import Profile
                Profile.objects.create(
                    user=user,
                    status='online',
                    bio=f'System generated {account_type} account for testing',
                    last_seen=timezone.now()
                )

                # Show account type with emoji
                type_emoji = '👑' if user_type == 1 else '🛡️' if user_type == 2 else '🎓'
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{type_emoji} Created {account_type}: {username}'
                        f'\n   📧 {account_data["email"]}'
                        f'\n   🔑 {password}'
                        f'\n'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Failed to create {account_type} account {username}: {str(e)}'
                )
            )
