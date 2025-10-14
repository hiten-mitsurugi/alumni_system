#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
import json

def test_achievement_api():
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
        
        # Test data - simulating what the frontend sends
        test_data = {
            'title': 'API Test Achievement',
            'type': 'certification',
            'description': 'Test description from API',
            'organization': 'Test Org',
            'url': 'https://example.com/cert',
            'is_featured': True
        }
        
        print("🧪 Testing Achievement API endpoint...")
        print(f"📤 Sending data: {test_data}")
        
        # Send POST request to create achievement
        response = client.post('/api/auth/achievements/', data=test_data)
        
        print(f"📥 Response status: {response.status_code}")
        print(f"📥 Response content: {response.content.decode()}")
        
        if response.status_code == 201:
            response_data = json.loads(response.content.decode())
            achievement_id = response_data.get('id')
            
            print(f"✅ Achievement created with ID: {achievement_id}")
            print(f"✅ Response data: {response_data}")
            
            # Clean up - delete the test achievement
            from auth_app.models import Achievement
            Achievement.objects.filter(id=achievement_id).delete()
            print("🗑️  Cleaned up test achievement")
            
        else:
            print(f"❌ Failed to create achievement")
            
    except Exception as e:
        print(f"❌ Error testing API: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_achievement_api()