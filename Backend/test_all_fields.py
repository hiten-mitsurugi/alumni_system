#!/usr/bin/env python
"""
Test what happens when we create an achievement with all fields via Django shell
"""
import os
import sys
import django
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

# Setup Django
sys.path.insert(0, '/c/Users/USER/OneDrive/Desktop/Thesis/development/alumni_system/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import Achievement
from auth_app.serializers import AchievementSerializer
from auth_app.views import AchievementListCreateView

User = get_user_model()

def test_achievement_with_all_fields():
    print("🔬 Testing achievement creation with ALL fields...")
    
    try:
        # Get user (use the one who created the recent achievement)
        user = User.objects.get(email='osorioroman101@gmail.com')
        print(f"✅ Using user: {user.username} (ID: {user.id})")
        
        # Create a proper test
        factory = RequestFactory()
        request = factory.post('/api/auth/achievements/')
        request.user = user
        
        view = AchievementListCreateView()
        view.request = request
        
        # Create test file
        test_file = SimpleUploadedFile(
            "test_certificate.pdf",
            b"PDF content here",
            content_type="application/pdf"
        )
        
        # This simulates exactly what the frontend should send
        data = {
            'title': 'Complete Test Achievement',
            'type': 'certification',  # This should NOT be empty!
            'description': 'This is a complete test with all fields filled',
            'organization': 'Test Organization Inc',
            'date_achieved': '2024-06-15',
            'url': 'https://testcertificate.example.com',
            'is_featured': True,
            'attachment': test_file
        }
        
        print("\n📋 Creating achievement with data:")
        for key, value in data.items():
            if key == 'attachment':
                print(f"  {key}: {type(value)} - {getattr(value, 'name', 'No name')}")
            else:
                print(f"  {key}: {value} ({type(value)})")
        
        # Use serializer with the data
        serializer = AchievementSerializer(data=data)
        
        if serializer.is_valid():
            print("\n✅ Serializer validation passed")
            
            # Use view's perform_create to set user
            view.perform_create(serializer)
            
            achievement = serializer.instance
            print(f"\n✅ Achievement created with ID: {achievement.id}")
            
            # Check what was saved
            saved = Achievement.objects.get(id=achievement.id)
            print(f"\n📋 What was actually saved:")
            print(f"  Title: '{saved.title}'")
            print(f"  Type: '{saved.type}' (length: {len(saved.type)})")
            print(f"  Organization: '{saved.organization}'")
            print(f"  Date: {saved.date_achieved}")
            print(f"  URL: '{saved.url}' (length: {len(saved.url)})")
            print(f"  Description: '{saved.description}'")
            print(f"  Attachment: '{saved.attachment}'")
            print(f"  Is Featured: {saved.is_featured}")
            
            # Test the serializer output (what API returns)
            output_serializer = AchievementSerializer(saved)
            print(f"\n📤 API would return:")
            for key, value in output_serializer.data.items():
                print(f"  {key}: {value}")
                
        else:
            print(f"❌ Serializer validation failed: {serializer.errors}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_achievement_with_all_fields()