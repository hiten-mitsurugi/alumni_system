#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import Achievement, CustomUser

def test_achievement_creation():
    try:
        # Get first user
        user = CustomUser.objects.first()
        if not user:
            print("❌ No users found")
            return
            
        print(f"👤 Testing with user: {user.username}")
        
        # Test creating an achievement with all fields
        achievement = Achievement.objects.create(
            user=user,
            title="Test Achievement",
            type="award",  
            description="Test description",
            organization="Test Organization",
            url="https://example.com/test",
            is_featured=True
        )
        
        print(f"✅ Created achievement with ID: {achievement.id}")
        print(f"   Title: {achievement.title}")
        print(f"   Type: {achievement.type}")
        print(f"   URL: {achievement.url}")
        print(f"   Organization: {achievement.organization}")
        print(f"   Attachment: {achievement.attachment}")
        
        # Now fetch it back to confirm it was saved
        saved_achievement = Achievement.objects.get(id=achievement.id)
        print(f"\n✅ Retrieved achievement from database:")
        print(f"   Title: {saved_achievement.title}")
        print(f"   Type: {saved_achievement.type}")
        print(f"   URL: {saved_achievement.url}")
        print(f"   Organization: {saved_achievement.organization}")
        print(f"   Attachment: {saved_achievement.attachment}")
        
        # Delete the test achievement
        achievement.delete()
        print(f"\n🗑️  Cleaned up test achievement")
        
    except Exception as e:
        print(f"❌ Error testing achievement creation: {e}")

if __name__ == "__main__":
    test_achievement_creation()