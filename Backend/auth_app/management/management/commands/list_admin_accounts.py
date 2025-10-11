from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'List all administrative accounts in the system'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='Show all users including alumni'
        )

    def handle(self, *args, **options):
        show_all = options['all']
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📋 === ADMINISTRATIVE ACCOUNTS ===\n'
            )
        )

        # Filter users by type
        if show_all:
            users = User.objects.all().order_by('user_type', 'username')
        else:
            users = User.objects.filter(user_type__in=[1, 2]).order_by('user_type', 'username')

        user_type_names = {1: 'Super Admin', 2: 'Admin', 3: 'Alumni'}
        user_type_emojis = {1: '👑', 2: '🛡️', 3: '🎓'}

        current_type = None
        count_by_type = {1: 0, 2: 0, 3: 0}

        for user in users:
            count_by_type[user.user_type] += 1
            
            # Show section header for each user type
            if current_type != user.user_type:
                current_type = user.user_type
                type_name = user_type_names.get(user.user_type, 'Unknown')
                type_emoji = user_type_emojis.get(user.user_type, '❓')
                
                self.stdout.write(
                    self.style.HTTP_INFO(
                        f'\n{type_emoji} {type_name} Accounts:'
                    )
                )

            # User status indicators
            status_indicators = []
            if user.is_superuser:
                status_indicators.append('🔑')
            if user.is_staff:
                status_indicators.append('⚙️')
            if user.is_approved:
                status_indicators.append('✅')
            if not user.is_active:
                status_indicators.append('❌')

            status_str = ' '.join(status_indicators) if status_indicators else '⚪'

            self.stdout.write(
                f'   {status_str} {user.username:15} | {user.email:25} | {user.school_id:10} | {user.first_name} {user.last_name}'
            )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n📊 === SUMMARY ===\n'
                f'👑 Super Admins: {count_by_type[1]}\n'
                f'🛡️  Admins: {count_by_type[2]}\n'
                f'🎓 Alumni: {count_by_type[3]}\n'
                f'📊 Total Users: {sum(count_by_type.values())}\n'
            )
        )

        self.stdout.write(
            self.style.HTTP_INFO(
                f'🔑 = Superuser | ⚙️ = Staff | ✅ = Approved | ❌ = Inactive\n'
            )
        )
