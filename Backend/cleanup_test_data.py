import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser, Following

# Remove the test connection created earlier
print('=== CLEANING UP TEST DATA ===')
roman = CustomUser.objects.get(id=3)
jane = CustomUser.objects.get(id=4)

# Delete Roman -> Jane connection if it exists
deleted_count = Following.objects.filter(
    follower=roman,
    following=jane
).delete()[0]

if deleted_count > 0:
    print(f'✅ Deleted {deleted_count} connection(s): Roman -> Jane')
else:
    print('ℹ️  No connection found from Roman to Jane')

# Show final state
print('\n=== FINAL DATABASE STATE ===')
all_following = Following.objects.all()
print(f'Total Following relationships: {all_following.count()}')

for f in all_following:
    print(f'  {f.follower.username} -> {f.following.username} (Status: {f.status})')

if all_following.count() == 0:
    print('  (No relationships)')

print('\n✅ Cleanup complete!')
