#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.serializers import AchievementSerializer
from auth_app.models import Achievement, CustomUser

def test_achievement_serializer():
    try:
        # Get first user
        user = CustomUser.objects.first()
        if not user:
            print("❌ No users found")
            return
            
        print(f"👤 Testing with user: {user.username}")
        
        # Test data
        test_data = {
            'title': 'Serializer Test Achievement',
            'type': 'certification',
            'description': 'Test description',
            'organization': 'Test Org',
            'date_achieved': '2024-05-15',
            'url': 'https://example.com/test',
            'is_featured': True,
            'user': user.id
        }
        
        print(f"📤 Testing serializer with data: {test_data}")
        
        # Test serializer validation
        serializer = AchievementSerializer(data=test_data)
        
        print(f"📝 Serializer is_valid: {serializer.is_valid()}")
        
        if not serializer.is_valid():
            print(f"❌ Serializer errors: {serializer.errors}")
            return
            
        # Save the object with user
        achievement = serializer.save(user=user)
        
        print(f"✅ Achievement saved with ID: {achievement.id}")
        print(f"🔍 Saved data:")
        print(f"   Title: {achievement.title}")
        print(f"   Type: {achievement.type}")
        print(f"   Description: {achievement.description}")
        print(f"   Organization: {achievement.organization}")
        print(f"   Date Achieved: {achievement.date_achieved}")
        print(f"   URL: {achievement.url}")
        print(f"   Is Featured: {achievement.is_featured}")
        print(f"   User: {achievement.user}")
        
        # Test serializer output
        output_serializer = AchievementSerializer(achievement)
        print(f"📤 Serializer output: {output_serializer.data}")
        
        # Clean up
        achievement.delete()
        print("🗑️  Cleaned up test achievement")
        
    except Exception as e:
        print(f"❌ Error testing serializer: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_achievement_serializer()