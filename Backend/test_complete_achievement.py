#!/usr/bin/env python
import os
import django
import sys
import json
from io import BytesIO
from PIL import Image

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

def test_achievement_with_all_fields():
    try:
        client = Client()
        User = get_user_model()
        
        # Get or create a test user
        user = User.objects.filter(username='superadmin').first()
        if not user:
            print("❌ No superadmin user found")
            return
            
        # Login the user
        client.force_login(user)
        
        # Create a simple test image file
        image = Image.new('RGB', (100, 100), color='red')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        test_file = SimpleUploadedFile(
            "test_certificate.jpg",
            image_io.read(),
            content_type="image/jpeg"
        )
        
        # Test data with ALL fields
        test_data = {
            'title': 'Complete Test Achievement',
            'type': 'award',
            'description': 'This is a test achievement with all fields filled',
            'organization': 'Test University',
            'date_achieved': '2024-05-15',
            'url': 'https://example.com/certificate-verification',
            'is_featured': True,
            'attachment': test_file
        }
        
        print("🧪 Testing Achievement API with ALL fields...")
        print(f"📤 Sending data: {dict((k, v if k != 'attachment' else 'test_certificate.jpg') for k, v in test_data.items())}")
        
        # Send POST request to create achievement
        response = client.post('/api/auth/achievements/', data=test_data, format='multipart')
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 201:
            response_data = json.loads(response.content.decode())
            achievement_id = response_data.get('id')
            
            print(f"✅ Achievement created with ID: {achievement_id}")
            print(f"✅ Full Response data:")
            for key, value in response_data.items():
                print(f"   {key}: {value}")
            
            # Now fetch the achievement back from database to verify all fields were saved
            from auth_app.models import Achievement
            saved_achievement = Achievement.objects.get(id=achievement_id)
            
            print(f"\n🔍 Verifying database record:")
            print(f"   Title: {saved_achievement.title}")
            print(f"   Type: {saved_achievement.type}")
            print(f"   Description: {saved_achievement.description}")
            print(f"   Organization: {saved_achievement.organization}")
            print(f"   Date Achieved: {saved_achievement.date_achieved}")
            print(f"   URL: {saved_achievement.url}")
            print(f"   Is Featured: {saved_achievement.is_featured}")
            print(f"   Attachment: {saved_achievement.attachment}")
            
            # Check which fields are missing or empty
            missing_fields = []
            if not saved_achievement.title: missing_fields.append('title')
            if not saved_achievement.type: missing_fields.append('type')
            if not saved_achievement.description: missing_fields.append('description')
            if not saved_achievement.organization: missing_fields.append('organization')
            if not saved_achievement.date_achieved: missing_fields.append('date_achieved')
            if not saved_achievement.url: missing_fields.append('url')
            if not saved_achievement.attachment: missing_fields.append('attachment')
            
            if missing_fields:
                print(f"❌ Missing/empty fields: {missing_fields}")
            else:
                print("✅ All fields saved successfully!")
            
            # Clean up - delete the test achievement
            saved_achievement.delete()
            print("🗑️  Cleaned up test achievement")
            
        else:
            print(f"❌ Failed to create achievement")
            print(f"❌ Response content: {response.content.decode()}")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_achievement_with_all_fields()