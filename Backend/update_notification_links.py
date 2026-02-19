import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from notifications_app.models import Notification

print('=== UPDATING OLD NOTIFICATION LINKS ===')

# Find all notifications with old /alumni/connections link
old_notifications = Notification.objects.filter(link_route='/alumni/connections')

print(f'Found {old_notifications.count()} notifications with old link')

if old_notifications.count() > 0:
    # Update them to new link
    updated_count = old_notifications.update(link_route='/alumni/my-mates')
    print(f'✅ Updated {updated_count} notifications to use /alumni/my-mates')
    
    # Show some examples
    print('\nUpdated notifications:')
    for notif in Notification.objects.filter(link_route='/alumni/my-mates')[:5]:
        print(f'  - {notif.title}: {notif.link_route} (params: {notif.link_params})')
else:
    print('✅ No old notifications found - all links are up to date')

print('\n=== CURRENT NOTIFICATION LINKS ===')
unique_routes = Notification.objects.values_list('link_route', flat=True).distinct()
for route in unique_routes:
    count = Notification.objects.filter(link_route=route).count()
    print(f'  {route}: {count} notifications')
