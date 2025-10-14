#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import Achievement

def check_latest_achievements():
    """Check the latest achievements to verify fields are being saved"""
    print("🔍 LATEST ACHIEVEMENT VERIFICATION")
    print("=" * 60)
    
    try:
        # Get the latest 5 achievements
        latest_achievements = Achievement.objects.all().order_by('-created_at')[:5]
        
        if not latest_achievements:
            print("❌ No achievements found in database")
            return
            
        print(f"📊 Found {latest_achievements.count()} achievements")
        print()
        
        for i, achievement in enumerate(latest_achievements, 1):
            print(f"🏆 Achievement #{i} (ID: {achievement.id})")
            print(f"   Title: {achievement.title}")
            print(f"   Type: '{achievement.type}' {'✅' if achievement.type else '❌ EMPTY'}")
            print(f"   URL: {achievement.url} {'✅' if achievement.url else '❌ EMPTY'}")
            print(f"   Attachment: {achievement.attachment} {'✅' if achievement.attachment else '❌ EMPTY'}")
            print(f"   Organization: {achievement.organization}")
            print(f"   Is Featured: {achievement.is_featured}")
            print(f"   Created: {achievement.created_at}")
            print(f"   User: {achievement.user.username}")
            
            # Count missing critical fields
            missing_fields = []
            if not achievement.type: missing_fields.append('type')
            if not achievement.url: missing_fields.append('url')
            if not achievement.attachment: missing_fields.append('attachment')
            
            if missing_fields:
                print(f"   ⚠️  Missing: {', '.join(missing_fields)}")
            else:
                print(f"   ✅ All critical fields present!")
            print()
            
    except Exception as e:
        print(f"❌ Error checking achievements: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_latest_achievements()