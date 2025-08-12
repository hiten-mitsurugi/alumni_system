#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser
from auth_app.serializers import UserDetailSerializer
from rest_framework_simplejwt.tokens import RefreshToken

def test_admin_api():
    print("=== Testing Admin API Authentication ===")
    
    try:
        admin_user = CustomUser.objects.get(email="admin@alumni.com")
        print(f"Admin user found: {admin_user.email}")
        
        # Generate JWT token for admin
        refresh = RefreshToken.for_user(admin_user)
        access_token = str(refresh.access_token)
        
        print(f"Generated access token: {access_token[:50]}...")
        
        # Now test the API endpoint manually
        import requests
        
        url = "http://127.0.0.1:8000/api/user/profile/"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        # Test GET request
        print("\n=== Testing GET /api/user/profile/ ===")
        response = requests.get(url, headers=headers)
        print(f"GET Status: {response.status_code}")
        if response.status_code == 200:
            print("GET Success! Current user data:")
            user_data = response.json()
            print(f"  - Name: {user_data.get('first_name')} {user_data.get('last_name')}")
            print(f"  - Email: {user_data.get('email')}")
            print(f"  - User Type: {user_data.get('user_type')}")
        else:
            print(f"GET Failed: {response.text}")
        
        # Test PUT request
        print("\n=== Testing PUT /api/user/profile/ ===")
        update_data = {
            "first_name": "Updated Admin",
            "contact_number": "123-456-7890"
        }
        
        put_headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        put_response = requests.put(url, json=update_data, headers=put_headers)
        print(f"PUT Status: {put_response.status_code}")
        if put_response.status_code == 200:
            print("PUT Success! Updated user data:")
            updated_data = put_response.json()
            print(f"  - Name: {updated_data.get('first_name')} {updated_data.get('last_name')}")
            print(f"  - Contact: {updated_data.get('contact_number')}")
        else:
            print(f"PUT Failed: {put_response.text}")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_admin_api()
