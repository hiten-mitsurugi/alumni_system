from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
import getpass

User = get_user_model()

class Command(BaseCommand):
    help = 'Reset admin account passwords or create new admin accounts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to reset password for'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='New password (will prompt if not provided)'
        )
        parser.add_argument(
            '--create',
            action='store_true',
            help='Create new admin account instead of resetting existing one'
        )
        parser.add_argument(
            '--superuser',
            action='store_true',
            help='Make the account a superuser (for --create only)'
        )

    def handle(self, *args, **options):
        username = options['username']
        password = options['password']
        create = options['create']
        make_superuser = options['superuser']

        if not username:
            username = input('Enter username: ')

        if not password:
            password = getpass.getpass('Enter password: ')

        if create:
            self.create_admin_account(username, password, make_superuser)
        else:
            self.reset_password(username, password)

    def reset_password(self, username, password):
        """Reset password for existing user"""
        try:
            user = User.objects.get(username=username)
            
            if user.user_type not in [1, 2]:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠️  User {username} is not an admin account (type: {user.get_user_type_display()})'
                    )
                )
                confirm = input('Continue anyway? (y/N): ')
                if confirm.lower() != 'y':
                    return

            user.set_password(password)
            user.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Password reset successfully for {username}\n'
                    f'   👤 User Type: {user.get_user_type_display()}\n'
                    f'   📧 Email (for login): {user.email}\n'
                    f'   🔑 New Password: {password}\n'
                    f'   🚨 IMPORTANT: Login with EMAIL, not username!\n'
                )
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ User {username} does not exist.\n'
                    f'   Use --create flag to create a new account.\n'
                )
            )

    def create_admin_account(self, username, password, make_superuser):
        """Create new admin account"""
        try:
            with transaction.atomic():
                if User.objects.filter(username=username).exists():
                    self.stdout.write(
                        self.style.ERROR(
                            f'❌ User {username} already exists.\n'
                            f'   Use without --create flag to reset password.\n'
                        )
                    )
                    return

                # Determine user type
                user_type = 1 if make_superuser else 2
                type_name = 'Super Admin' if make_superuser else 'Admin'

                # Generate unique school_id
                import random
                school_id = f'ADM{user_type}{random.randint(1000, 9999)}'
                while User.objects.filter(school_id=school_id).exists():
                    school_id = f'ADM{user_type}{random.randint(1000, 9999)}'

                # Create user
                user = User.objects.create_user(
                    username=username,
                    email=f'{username}@alumni.system',
                    password=password,
                    first_name=username.title(),
                    last_name='Administrator',
                    user_type=user_type,
                    school_id=school_id,
                    program='Administration',
                    is_approved=True,
                    is_active=True,
                    is_staff=True,
                    is_superuser=make_superuser,
                    # Required fields
                    gender='prefer_not_to_say',
                    birth_date='1990-01-01',
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

                # Create profile
                from auth_app.models import Profile
                from django.utils import timezone
                Profile.objects.create(
                    user=user,
                    status='online',
                    bio=f'System generated {type_name} account',
                    last_seen=timezone.now()
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ Created new {type_name} account:\n'
                        f'   👤 Username: {username}\n'
                        f'   📧 Email: {user.email}\n'
                        f'   🆔 School ID: {school_id}\n'
                        f'   🔑 Password: {password}\n'
                        f'   📋 Type: {type_name} (Level {user_type})\n'
                        f'   ✅ Status: Active & Approved\n'
                    )
                )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Failed to create admin account: {str(e)}'
                )
            )
