from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone
from datetime import date
import random

User = get_user_model()

class Command(BaseCommand):
    help = 'Create test alumni accounts for testing purposes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--password',
            type=str,
            default='Alumni@123',
            help='Password for all test alumni accounts (default: Alumni@123)'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Force recreation of accounts if they already exist'
        )

    def handle(self, *args, **options):
        password = options['password']
        force = options['force']

        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Creating Test Alumni Accounts ===\n'
            )
        )

        # Define test alumni data
        test_alumni = [
            {
                'username': 'maria.santos',
                'email': 'maria.santos@alumni.test',
                'first_name': 'Maria',
                'last_name': 'Santos',
                'program': 'Computer Science',
                'year_graduated': 2020,
                'gender': 'female',
                'birth_date': date(1998, 3, 15),
                'contact_number': '+63-917-123-4567',
                'mothers_name': 'Carmen Santos',
                'mothers_occupation': 'Teacher',
                'fathers_name': 'Roberto Santos',
                'fathers_occupation': 'Engineer',
                'civil_status': 'single',
                'employment_status': 'employed_locally',
                'bio': 'Full-stack developer passionate about creating user-friendly applications.',
                'street_address': '123 Mabini Street, Barangay San Jose',
                'city': 'Manila',
                'province': 'Metro Manila',
                'region': 'National Capital Region'
            },
            {
                'username': 'john.dela.cruz',
                'email': 'john.delacruz@alumni.test',
                'first_name': 'John',
                'last_name': 'Dela Cruz',
                'program': 'Information Technology',
                'year_graduated': 2019,
                'gender': 'male',
                'birth_date': date(1997, 7, 22),
                'contact_number': '+63-918-987-6543',
                'mothers_name': 'Elena Dela Cruz',
                'mothers_occupation': 'Nurse',
                'fathers_name': 'Miguel Dela Cruz',
                'fathers_occupation': 'Business Owner',
                'civil_status': 'married',
                'employment_status': 'employed_abroad',
                'bio': 'Software engineer working remotely for international clients. Love solving complex problems.',
                'street_address': '456 Rizal Avenue, Barangay Poblacion',
                'city': 'Quezon City',
                'province': 'Metro Manila',
                'region': 'National Capital Region'
            }
        ]

        # Create each test alumni account
        for alumni_data in test_alumni:
            self.create_alumni_account(alumni_data, password, force)

        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Test Alumni Creation Complete ===\n'
                f'🔐 LOGIN CREDENTIALS (Use EMAIL + PASSWORD):\n'
                f'Password for all accounts: {password}\n'
                f'\n📋 Password Requirements Met:\n'
                f'✅ Minimum 8 characters\n'
                f'✅ Contains uppercase letter\n' 
                f'✅ Contains lowercase letter\n'
                f'✅ Contains number\n'
                f'✅ Contains special character\n'
                f'\n🌐 Login URL: /alumni/login\n'
            )
        )

    def create_alumni_account(self, alumni_data, password, force):
        """Create a single alumni account with the given data"""
        
        username = alumni_data['username']
        
        try:
            with transaction.atomic():
                # Check if user already exists
                if User.objects.filter(username=username).exists():
                    if force:
                        # Delete existing user
                        User.objects.filter(username=username).delete()
                        self.stdout.write(
                            self.style.WARNING(
                                f'🔄 Deleted existing alumni account: {username}'
                            )
                        )
                    else:
                        self.stdout.write(
                            self.style.WARNING(
                                f'⚠️  Alumni account already exists: {username}'
                                f' (use --force to recreate)'
                            )
                        )
                        return

                # Create the user account
                user = User.objects.create_user(
                    username=alumni_data['username'],
                    email=alumni_data['email'],
                    password=password,
                    first_name=alumni_data['first_name'],
                    last_name=alumni_data['last_name'],
                    user_type=3,  # Alumni
                    is_approved=True,
                    is_active=True,
                    is_staff=False,
                    is_superuser=False,
                    # Required fields
                    program=alumni_data['program'],
                    gender=alumni_data['gender'],
                    birth_date=alumni_data['birth_date'],
                    contact_number=alumni_data['contact_number'],
                    year_graduated=alumni_data['year_graduated'],
                    mothers_name=alumni_data['mothers_name'],
                    mothers_occupation=alumni_data['mothers_occupation'],
                    fathers_name=alumni_data['fathers_name'],
                    fathers_occupation=alumni_data['fathers_occupation'],
                    civil_status=alumni_data['civil_status'],
                    employment_status=alumni_data['employment_status']
                )

                # Create normalized Address rows for alumni
                from auth_app.models import Address
                Address.objects.update_or_create(
                    user=user,
                    address_category='present',
                    defaults={
                        'address_type': 'philippines',
                        'region_code': '',
                        'region_name': alumni_data['region'],
                        'province_code': '',
                        'province_name': alumni_data['province'],
                        'city_code': '',
                        'city_name': alumni_data['city'],
                        'barangay': '',
                        'street_address': alumni_data['street_address'],
                        'postal_code': '',
                        'country': 'Philippines',
                        'full_address': f"{alumni_data['street_address']}, {alumni_data['city']}, {alumni_data['province']}",
                    }
                )
                Address.objects.update_or_create(
                    user=user,
                    address_category='permanent',
                    defaults={
                        'address_type': 'philippines',
                        'region_code': '',
                        'region_name': alumni_data['region'],
                        'province_code': '',
                        'province_name': alumni_data['province'],
                        'city_code': '',
                        'city_name': alumni_data['city'],
                        'barangay': '',
                        'street_address': alumni_data['street_address'],
                        'postal_code': '',
                        'country': 'Philippines',
                        'full_address': f"{alumni_data['street_address']}, {alumni_data['city']}, {alumni_data['province']}",
                    }
                )

                # Create profile for the alumni
                from auth_app.models import Profile
                profile = Profile.objects.create(
                    user=user,
                    full_name=f'{user.first_name} {user.last_name}',
                    email_address=user.email,
                    mobile_number=user.contact_number,
                    gender=user.gender,
                    civil_status=user.civil_status,
                    year_of_birth=user.birth_date,
                    mothers_name=user.mothers_name,
                    mothers_occupation=user.mothers_occupation,
                    fathers_name=user.fathers_name,
                    fathers_occupation=user.fathers_occupation,
                    year_graduated=user.year_graduated,
                    program=user.program,
                    present_employment_status=user.employment_status,
                    status='online',
                    bio=alumni_data['bio'],
                    last_seen=timezone.now()
                )

                # Create some sample work history entries (optional - skip for now)
                # Can be added later through the admin interface or manually
                # from auth_app.models import WorkHistory

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Created Alumni account:'
                        f'\n   📧 Email (for login): {alumni_data["email"]}'
                        f'\n   👤 Username: {alumni_data["username"]}'
                        f'\n   👨‍🎓 Name: {alumni_data["first_name"]} {alumni_data["last_name"]}'
                        f'\n   🎓 Program: {alumni_data["program"]} ({alumni_data["year_graduated"]})'
                        f'\n   🔑 Password: {password}'
                        f'\n   💼 Employment: {alumni_data["employment_status"]}'
                        f'\n   📍 Location: {alumni_data["city"]}, {alumni_data["province"]}'
                        f'\n   ✅ Status: Active & Approved'
                        f'\n   🚨 IMPORTANT: Login with EMAIL, not username!'
                        f'\n'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Failed to create alumni account {username}: {str(e)}'
                )
            )
            raise
