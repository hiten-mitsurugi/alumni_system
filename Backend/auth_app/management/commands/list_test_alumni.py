from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'List test alumni accounts'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Test Alumni Account Status ===\n'
            )
        )

        try:
            test_users = User.objects.filter(
                user_type=3, 
                username__in=['maria.santos', 'john.dela.cruz']
            )

            if not test_users.exists():
                self.stdout.write(
                    self.style.WARNING(
                        '⚠️  No test alumni accounts found.'
                    )
                )
                return

            for user in test_users:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✅ {user.first_name} {user.last_name}\n'
                        f'   👤 Username: {user.username}\n'
                        f'   📧 Email: {user.email}\n'
                        f'   🎓 Program: {user.program} ({user.year_graduated})\n'
                        f'   📱 Contact: {user.contact_number}\n'
                        f'   🔐 Active: {user.is_active}\n'
                        f'   ✅ Approved: {user.is_approved}\n'
                        f'   💼 Employment: {user.employment_status}\n'
                        f'   📍 Type: {user.get_user_type_display()}\n'
                    )
                )

            self.stdout.write(
                self.style.SUCCESS(
                    f'\n=== Summary ===\n'
                    f'Found {test_users.count()} test alumni accounts\n'
                    f'All accounts are ready for testing!\n'
                    f'\n🔐 Login Credentials:\n'
                    f'Password for all: Alumni@123\n'
                    f'Login with EMAIL (not username)\n'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Error listing test alumni: {str(e)}'
                )
            )