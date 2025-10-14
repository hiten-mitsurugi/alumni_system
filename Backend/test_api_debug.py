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

def test_api_debug():
    """Focused test to see debug output from API"""
    print("🧪 FOCUSED API DEBUG TEST")
    print("=" * 50)
    
    try:
        client = Client()
        User = get_user_model()
        user = User.objects.filter(username='superadmin').first()
        
        if not user:
            print("❌ No superadmin user found")
            return
            
        # Login the user
        client.force_login(user)
        
        # Create a simple test file
        image = Image.new('RGB', (50, 50), color='green')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        test_file = SimpleUploadedFile(
            "debug_test.jpg",
            image_io.read(),
            content_type="image/jpeg"
        )
        
        # Test data for API - focus on the critical missing fields
        test_data = {
            'title': 'DEBUG Test Achievement',
            'type': 'academic',  # This field is missing
            'url': 'https://debug-test.example.com/verify',  # This field is missing
            'attachment': test_file,  # This field is missing
            'description': 'Debug test to see what happens to critical fields',
            'organization': 'DEBUG University',
            'is_featured': False
        }
        
        print(f"📤 Sending critical fields test:")
        for key, value in test_data.items():
            if key == 'attachment':
                print(f"   {key}: {value.name} ({value.content_type})")
            else:
                print(f"   {key}: {value}")
        
        print("\n📡 Making API request...")
        
        # Send POST request and capture any debug output
        response = client.post('/api/auth/achievements/', data=test_data, format='multipart')
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response headers: {dict(response.items())}")
        
        if response.status_code == 201:
            response_data = json.loads(response.content.decode())
            print(f"✅ Response data: {response_data}")
        else:
            print(f"❌ Error response: {response.content.decode()}")
            
    except Exception as e:
        print(f"❌ Debug test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_api_debug()