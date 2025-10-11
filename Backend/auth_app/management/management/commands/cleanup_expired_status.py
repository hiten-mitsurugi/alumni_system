from django.core.management.base import BaseCommand
from auth_app.status_cache import UserStatusCache
import time

class Command(BaseCommand):
    help = 'Clean up expired user statuses from Redis'

    def add_arguments(self, parser):
        parser.add_argument(
            '--interval',
            type=int,
            default=60,
            help='Cleanup interval in seconds (default: 60)'
        )
        parser.add_argument(
            '--run-once',
            action='store_true',
            help='Run cleanup once and exit'
        )

    def handle(self, *args, **options):
        interval = options['interval']
        run_once = options['run_once']
        
        if run_once:
            self.stdout.write('Running status cleanup once...')
            cleaned = UserStatusCache.cleanup_offline_users()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully cleaned up expired statuses')
            )
            return
        
        self.stdout.write(f'Starting status cleanup with {interval}s interval...')
        self.stdout.write('Press Ctrl+C to stop')
        
        try:
            while True:
                cleaned = UserStatusCache.cleanup_offline_users()
                self.stdout.write(f'Cleanup completed')
                time.sleep(interval)
        except KeyboardInterrupt:
            self.stdout.write('\nStatus cleanup stopped')
