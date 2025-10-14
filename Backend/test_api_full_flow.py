#!/usr/bin/env python
"""
Full API test to simulate exactly what the frontend does
"""
import os
import sys
import django
from django.test import Client
from django.contrib.auth import get_user_model
import json
from io import BytesIO

# Setup Django
sys.path.insert(0, '/c/Users/USER/OneDrive/Desktop/Thesis/development/alumni_system/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

User = get_user_model()

def test_achievement_api_full_flow():
    print("🔬 Testing full API flow like frontend...")
    
    # Create client and user
    client = Client()
    
    try:
        # Use existing test user with skills
        try:
            user = User.objects.get(username='test_skill_user')
            print(f"✅ Using existing test user: {user.username}")
        except User.DoesNotExist:
            # Try the admin user as fallback
            user = User.objects.get(username='admin')
            print(f"✅ Using admin user: {user.username}")
        
        # Set a known password for testing
        user.set_password('testpass123')
        user.save()
        
        # Login
        login_success = client.login(username=user.username, password='testpass123')
        print(f"✅ Login successful: {login_success}")
        
        if not login_success:
            print("❌ Login failed, cannot continue")
            return
        
        # Create a test file content
        test_file_content = b"Test attachment content"
        test_file = BytesIO(test_file_content)
        test_file.name = 'test_attachment.txt'
        
        # Prepare data exactly like frontend FormData
        post_data = {
            'title': 'API Test Achievement',
            'type': 'award',
            'description': 'Full API test description',
            'organization': 'API Test Org',
            'date_achieved': '2024-05-20',
            'url': 'https://api-test.example.com',
            'is_featured': 'true',  # String like frontend sends
            'attachment': test_file
        }
        
        print("\n📤 POST data being sent:")
        for key, value in post_data.items():
            if key == 'attachment':
                print(f"  {key}: {type(value)} - {getattr(value, 'name', 'No name')}")
            else:
                print(f"  {key}: {value} ({type(value)})")
        
        # Make POST request to create achievement
        response = client.post('/api/auth/achievements/', post_data)
        
        print(f"\n📥 Response Status: {response.status_code}")
        
        if response.status_code == 201:
            response_data = response.json()
            print(f"✅ Achievement created successfully!")
            print(f"📋 Response data:")
            for key, value in response_data.items():
                print(f"  {key}: {value}")
            
            achievement_id = response_data.get('id')
            
            # Now test GET to see what's returned
            print(f"\n🔍 Testing GET /api/auth/achievements/{achievement_id}/")
            get_response = client.get(f'/api/auth/achievements/{achievement_id}/')
            
            print(f"📥 GET Response Status: {get_response.status_code}")
            
            if get_response.status_code == 200:
                get_data = get_response.json()
                print(f"📋 GET Response data:")
                for key, value in get_data.items():
                    print(f"  {key}: {value}")
                
                # Check which fields are missing
                expected_fields = ['title', 'type', 'description', 'organization', 'date_achieved', 'url', 'attachment', 'is_featured']
                missing_fields = []
                for field in expected_fields:
                    if field not in get_data:
                        missing_fields.append(field)
                
                if missing_fields:
                    print(f"⚠️  Missing fields in GET response: {missing_fields}")
                else:
                    print("✅ All expected fields present in GET response")
            else:
                print(f"❌ GET request failed: {get_response.content.decode()}")
                
        else:
            print(f"❌ POST request failed: {response.content.decode()}")
            
        # Test GET list endpoint too
        print(f"\n🔍 Testing GET /api/auth/achievements/ (list)")
        list_response = client.get('/api/auth/achievements/')
        
        print(f"📥 LIST Response Status: {list_response.status_code}")
        
        if list_response.status_code == 200:
            list_data = list_response.json()
            if isinstance(list_data, list) and len(list_data) > 0:
                print(f"📋 First achievement in list:")
                for key, value in list_data[0].items():
                    print(f"  {key}: {value}")
            else:
                print("📭 No achievements in list response")
        
    except Exception as e:
        print(f"❌ Error during API test: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_achievement_api_full_flow()