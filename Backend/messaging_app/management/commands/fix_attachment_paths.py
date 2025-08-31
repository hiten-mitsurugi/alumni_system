from django.core.management.base import BaseCommand
from messaging_app.models import Attachment
import os

class Command(BaseCommand):
    help = 'Fix corrupted attachment file paths in the database'

    def handle(self, *args, **options):
        self.stdout.write('Starting to fix attachment paths...')
        
        attachments = Attachment.objects.all()
        fixed_count = 0
        
        for attachment in attachments:
            old_path = attachment.file.name
            self.stdout.write(f'Checking attachment {attachment.id}: {old_path}')
            
            # Check if path starts with /media/
            if old_path.startswith('/media/'):
                # Remove the /media/ prefix
                new_path = old_path[7:]  # Remove '/media/'
                
                # If it doesn't start with 'attachments/', add it
                if not new_path.startswith('attachments/'):
                    filename = os.path.basename(new_path)
                    new_path = f'attachments/{filename}'
                
                self.stdout.write(f'  Fixing: {old_path} -> {new_path}')
                
                # Update the file path directly in the database
                attachment.file.name = new_path
                attachment.save()
                fixed_count += 1
            else:
                self.stdout.write(f'  OK: {old_path}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully fixed {fixed_count} attachment paths')
        )
