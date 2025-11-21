"""
Clean up old notifications and fix actor data
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from notifications_app.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 80)
print("🧹 CLEANING UP NOTIFICATIONS")
print("=" * 80)

# Step 1: Count notifications without actors
notifications_without_actor = Notification.objects.filter(actor__isnull=True, type='post')
count = notifications_without_actor.count()

print(f"\n📊 Found {count} post notifications without actor")

if count > 0:
    print("\n❓ These notifications were created before the actor field was added.")
    print("   They will show 'System' as the actor name and no avatar.")
    print("\n Options:")
    print("   1. Delete them (recommended - clean start)")
    print("   2. Keep them (they'll show as system notifications)")
    
    choice = input("\n   Enter 1 to delete, 2 to keep: ").strip()
    
    if choice == '1':
        # Delete old notifications
        deleted_count, _ = notifications_without_actor.delete()
        print(f"\n✅ Deleted {deleted_count} old notifications")
    else:
        print(f"\n✅ Keeping {count} old notifications (they'll show as system notifications)")

# Step 2: Show current notifications
print("\n" + "=" * 80)
print("📋 CURRENT NOTIFICATIONS")
print("=" * 80)

current_notifications = Notification.objects.all().order_by('-created_at')[:5]

for notif in current_notifications:
    actor_info = f"{notif.actor.first_name} {notif.actor.last_name}" if notif.actor else "System"
    print(f"\nID {notif.id}: {notif.type}")
    print(f"   To: {notif.user.email}")
    print(f"   Actor: {actor_info}")
    print(f"   Title: {notif.title}")
    print(f"   Created: {notif.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

print("\n" + "=" * 80)
print("✅ Cleanup complete!")
print("=" * 80)
