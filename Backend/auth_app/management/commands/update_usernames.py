from django.core.management.base import BaseCommand
from auth_app.username_utils import update_existing_usernames

class Command(BaseCommand):
    help = 'Update all existing users to have name-based usernames instead of emails'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making actual changes',
        )

    def handle(self, *args, **options):
        if options['dry_run']:
            self.stdout.write('DRY RUN: Showing what would be changed...')
            from django.contrib.auth import get_user_model
            
            User = get_user_model()
            users_to_update = User.objects.filter(username__contains='@')
            
            self.stdout.write(f'Found {users_to_update.count()} users with email-based usernames:')
            
            for user in users_to_update:
                from auth_app.username_utils import generate_unique_username
                new_username = generate_unique_username(
                    user.first_name, 
                    user.last_name
                )
                self.stdout.write(f'  {user.username} -> {new_username}')
        else:
            self.stdout.write('Updating usernames...')
            update_existing_usernames()
            self.stdout.write(
                self.style.SUCCESS('Successfully updated usernames!')
            )
