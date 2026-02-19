import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser, Following

print('=== ALUMNI USERS ===')
alumni = CustomUser.objects.filter(user_type=3, is_approved=True)
for user in alumni:
    print(f'ID: {user.id}, Username: {user.username}, Email: {user.email}, Name: {user.first_name} {user.last_name}')

print(f'\nTotal approved alumni: {alumni.count()}')

print('\n=== FOLLOWING RELATIONSHIPS ===')
followings = Following.objects.all()
print(f'Total Following relationships: {followings.count()}')

if followings.count() > 0:
    print('\nAll relationships:')
    for f in followings:
        print(f'ID: {f.id}')
        print(f'  Follower: {f.follower.username} (ID: {f.follower.id}) -> Following: {f.following.username} (ID: {f.following.id})')
        print(f'  Status: {f.status}, Mutual: {f.is_mutual}, Created: {f.created_at}')
        print()
else:
    print('\n⚠️  No Following relationships found in database!')
    print('Users need to send connection requests to create relationships.')

print('\n=== INVITATION STATUS (PENDING) ===')
pending = Following.objects.filter(status='pending')
print(f'Pending invitations: {pending.count()}')
for inv in pending:
    print(f'  {inv.follower.username} -> {inv.following.username} (ID: {inv.id})')

print('\n=== ACCEPTED CONNECTIONS ===')
accepted = Following.objects.filter(status='accepted')
print(f'Accepted connections: {accepted.count()}')
for conn in accepted:
    print(f'  {conn.follower.username} <-> {conn.following.username} (Mutual: {conn.is_mutual})')
