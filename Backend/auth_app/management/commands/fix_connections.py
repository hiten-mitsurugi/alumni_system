"""
Management command to fix broken connections between users
Usage: python manage.py fix_connections
"""
from django.core.management.base import BaseCommand
from auth_app.models import Following, CustomUser


class Command(BaseCommand):
    help = 'Fix broken connections - ensure all accepted connections have is_mutual=True and reverse connections'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user1',
            type=int,
            help='First user ID to fix connection for',
        )
        parser.add_argument(
            '--user2',
            type=int,
            help='Second user ID to fix connection for',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Fix all connections in the database',
        )

    def handle(self, *args, **options):
        if options['user1'] and options['user2']:
            # Fix specific connection
            self.fix_specific_connection(options['user1'], options['user2'])
        elif options['all']:
            # Fix all connections
            self.fix_all_connections()
        else:
            self.stdout.write(self.style.ERROR('Please specify --user1 and --user2, or use --all'))

    def fix_specific_connection(self, user1_id, user2_id):
        """Fix connection between two specific users"""
        try:
            user1 = CustomUser.objects.get(id=user1_id)
            user2 = CustomUser.objects.get(id=user2_id)
            
            self.stdout.write(f'🔧 Fixing connection between {user1.username} (ID: {user1.id}) and {user2.username} (ID: {user2.id})')
            
            # Get or create both directions
            forward, f_created = Following.objects.get_or_create(
                follower=user1,
                following=user2,
                defaults={'status': 'accepted', 'is_mutual': True}
            )
            
            reverse, r_created = Following.objects.get_or_create(
                follower=user2,
                following=user1,
                defaults={'status': 'accepted', 'is_mutual': True}
            )
            
            # Update both to be mutual and accepted
            if not f_created:
                forward.status = 'accepted'
                forward.is_mutual = True
                forward.save()
            
            if not r_created:
                reverse.status = 'accepted'
                reverse.is_mutual = True
                reverse.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Forward: ID={forward.id}, mutual={forward.is_mutual}, status={forward.status}'))
            self.stdout.write(self.style.SUCCESS(f'✅ Reverse: ID={reverse.id}, mutual={reverse.is_mutual}, status={reverse.status}'))
            self.stdout.write(self.style.SUCCESS('✅ Connection fixed!'))
            
        except CustomUser.DoesNotExist as e:
            self.stdout.write(self.style.ERROR(f'❌ User not found: {e}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))

    def fix_all_connections(self):
        """Fix all connections in the database"""
        self.stdout.write('🔧 Fixing all connections...')
        
        # Get all Following records
        all_followings = Following.objects.all()
        total = all_followings.count()
        fixed = 0
        created = 0
        
        self.stdout.write(f'Found {total} Following records')
        
        # Process each connection
        processed_pairs = set()
        
        for following in all_followings:
            # Create a unique pair identifier (sorted to avoid duplicates)
            pair = tuple(sorted([following.follower_id, following.following_id]))
            
            if pair in processed_pairs:
                continue
            
            processed_pairs.add(pair)
            
            user1_id, user2_id = pair
            
            # Get or create both directions
            forward = Following.objects.filter(
                follower_id=user1_id,
                following_id=user2_id
            ).first()
            
            reverse = Following.objects.filter(
                follower_id=user2_id,
                following_id=user1_id
            ).first()
            
            # Only fix if at least one connection is accepted
            if (forward and forward.status == 'accepted') or (reverse and reverse.status == 'accepted'):
                # Ensure both directions exist
                if not forward:
                    forward = Following.objects.create(
                        follower_id=user1_id,
                        following_id=user2_id,
                        status='accepted',
                        is_mutual=True
                    )
                    created += 1
                    self.stdout.write(f'  ✨ Created forward connection: User {user1_id} → User {user2_id}')
                
                if not reverse:
                    reverse = Following.objects.create(
                        follower_id=user2_id,
                        following_id=user1_id,
                        status='accepted',
                        is_mutual=True
                    )
                    created += 1
                    self.stdout.write(f'  ✨ Created reverse connection: User {user2_id} → User {user1_id}')
                
                # Update both to be mutual and accepted
                needs_fix = False
                
                if forward.status != 'accepted' or not forward.is_mutual:
                    forward.status = 'accepted'
                    forward.is_mutual = True
                    forward.save()
                    needs_fix = True
                
                if reverse.status != 'accepted' or not reverse.is_mutual:
                    reverse.status = 'accepted'
                    reverse.is_mutual = True
                    reverse.save()
                    needs_fix = True
                
                if needs_fix:
                    fixed += 1
                    self.stdout.write(f'  🔧 Fixed connection between User {user1_id} and User {user2_id}')
        
        self.stdout.write(self.style.SUCCESS(f'\n✅ Complete!'))
        self.stdout.write(self.style.SUCCESS(f'   Fixed: {fixed} connection pairs'))
        self.stdout.write(self.style.SUCCESS(f'   Created: {created} new connections'))
        self.stdout.write(self.style.SUCCESS(f'   Total pairs processed: {len(processed_pairs)}'))
