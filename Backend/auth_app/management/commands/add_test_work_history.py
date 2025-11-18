from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from datetime import date

User = get_user_model()

class Command(BaseCommand):
    help = 'Add work history to test alumni accounts'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Adding Work History to Test Alumni ===\n'
            )
        )

        try:
            # Find our test alumni
            maria = User.objects.get(username='maria.santos')
            john = User.objects.get(username='john.dela.cruz')

            from auth_app.models import WorkHistory

            # Add work history for Maria
            work_maria = WorkHistory.objects.create(
                user=maria,
                occupation='Software Developer',
                employing_agency='Tech Solutions Inc.',
                classification='private',
                length_of_service='3 years',
                start_date=date(2020, 6, 1),
                is_current_job=True,
                description='Developing web applications using modern technologies like React, Django, and PostgreSQL'
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Added work history for Maria Santos: {work_maria}'
                )
            )

            # Add work history for John
            work_john = WorkHistory.objects.create(
                user=john,
                occupation='Senior Software Engineer',
                employing_agency='Global Tech Corp',
                classification='private',
                length_of_service='4 years',
                start_date=date(2019, 8, 1),
                is_current_job=True,
                description='Leading development team for international projects, specializing in cloud architecture and microservices'
            )

            self.stdout.write(
                self.style.SUCCESS(
                    f'✅ Added work history for John Dela Cruz: {work_john}'
                )
            )

        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(
                    '❌ Test alumni users not found. Please run create_test_alumni first.'
                )
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(
                    f'❌ Error adding work history: {str(e)}'
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Work History Addition Complete ===\n'
            )
        )