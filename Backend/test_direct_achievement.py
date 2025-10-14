#!/usr/bin/env python
"""
Test achievement creation directly without client login
"""
import os
import sys
import django
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django
sys.path.insert(0, '/c/Users/USER/OneDrive/Desktop/Thesis/development/alumni_system/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import Achievement
from auth_app.serializers import AchievementSerializer

User = get_user_model()

def test_achievement_direct():
    print("🔬 Testing achievement creation directly...")
    
    try:
        # Get existing user
        user = User.objects.get(username='test_skill_user')
        print(f"✅ Using user: {user.username} (ID: {user.id})")
        
        # Create test file
        test_file = SimpleUploadedFile(
            "test_achievement.txt",
            b"Test attachment content",
            content_type="text/plain"
        )
        
        # Create achievement data exactly like frontend would send
        achievement_data = {
            'title': 'Direct Test Achievement',
            'type': 'award',
            'description': 'Direct test description',
            'organization': 'Direct Test Org',
            'date_achieved': '2024-05-21',
            'url': 'https://direct-test.example.com',
            'is_featured': True,  # Boolean this time
            'attachment': test_file,
            'user': user.id
        }
        
        print("\n📋 Creating achievement with data:")
        for key, value in achievement_data.items():
            if key == 'attachment':
                print(f"  {key}: {type(value)} - {getattr(value, 'name', 'No name')}")
            else:
                print(f"  {key}: {value} ({type(value)})")
        
        # Use serializer to create
        serializer = AchievementSerializer(data=achievement_data)
        
        if serializer.is_valid():
            achievement = serializer.save()
            print(f"\n✅ Achievement created with ID: {achievement.id}")
            
            # Check what was actually saved
            saved_achievement = Achievement.objects.get(id=achievement.id)
            print(f"📋 Saved achievement data:")
            print(f"  ID: {saved_achievement.id}")
            print(f"  Title: {saved_achievement.title}")
            print(f"  Type: {saved_achievement.type}")
            print(f"  Description: {saved_achievement.description}")
            print(f"  Organization: {saved_achievement.organization}")
            print(f"  Date: {saved_achievement.date_achieved}")
            print(f"  URL: {saved_achievement.url}")
            print(f"  Is Featured: {saved_achievement.is_featured}")
            print(f"  Attachment: {saved_achievement.attachment}")
            print(f"  User: {saved_achievement.user}")
            
            # Now test serializer output (what API would return)
            output_serializer = AchievementSerializer(saved_achievement)
            print(f"\n📤 Serializer output (what API returns):")
            for key, value in output_serializer.data.items():
                print(f"  {key}: {value}")
            
            # Check if any fields are missing
            expected_fields = ['id', 'title', 'type', 'description', 'organization', 'date_achieved', 'url', 'attachment', 'is_featured', 'user']
            serializer_fields = list(output_serializer.data.keys())
            missing_fields = [f for f in expected_fields if f not in serializer_fields]
            extra_fields = [f for f in serializer_fields if f not in expected_fields]
            
            if missing_fields:
                print(f"⚠️  Missing fields in serializer output: {missing_fields}")
            if extra_fields:
                print(f"ℹ️  Extra fields in serializer output: {extra_fields}")
            if not missing_fields:
                print("✅ All expected fields present in serializer output")
                
        else:
            print(f"❌ Serializer validation failed: {serializer.errors}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_achievement_direct()