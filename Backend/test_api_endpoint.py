#!/usr/bin/env python
"""
Test the actual API endpoint using requests
"""
import requests
import os
from requests.auth import HTTPBasicAuth

def test_achievement_api():
    print("🔬 Testing Achievement API endpoint...")
    
    base_url = "http://127.0.0.1:8000"  # Assuming server runs on this port
    
    # Login first to get session/cookies
    login_data = {
        'username': 'test_skill_user',
        'password': 'testpass123'  # You may need to set this password first
    }
    
    session = requests.Session()
    
    # Try to login
    login_response = session.post(f"{base_url}/api/auth/login/", data=login_data)
    print(f"Login response: {login_response.status_code}")
    
    if login_response.status_code == 200:
        print("✅ Login successful")
        
        # Now try to create achievement
        files = {
            'attachment': ('test_file.txt', b'Test file content', 'text/plain')
        }
        
        data = {
            'title': 'API Endpoint Test',
            'type': 'certification',
            'description': 'Testing actual API endpoint',
            'organization': 'Test Org API',
            'date_achieved': '2024-05-22',
            'url': 'https://endpoint-test.example.com',
            'is_featured': 'true'
        }
        
        print(f"📤 Sending POST to /api/auth/achievements/")
        print(f"Data: {data}")
        print(f"Files: {list(files.keys())}")
        
        create_response = session.post(
            f"{base_url}/api/auth/achievements/",
            data=data,
            files=files
        )
        
        print(f"📥 Create response: {create_response.status_code}")
        
        if create_response.status_code == 201:
            response_data = create_response.json()
            print("✅ Achievement created via API!")
            print("📋 Response data:")
            for key, value in response_data.items():
                print(f"  {key}: {value}")
        else:
            print(f"❌ Create failed: {create_response.text}")
            
    else:
        print(f"❌ Login failed: {login_response.text}")

if __name__ == "__main__":
    print("⚠️  Make sure your Django server is running on http://127.0.0.1:8000")
    print("⚠️  You may need to set the password for test_skill_user first")
    print()
    test_achievement_api()