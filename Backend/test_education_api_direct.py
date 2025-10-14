#!/usr/bin/env python
"""
Test the education API endpoints directly to see what they return
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from auth_app.models import CustomUser, Education
import json

print("=== EDUCATION API ENDPOINT TEST ===")

# Create a test client
client = Client()

try:
    # Get user 8 (Prince Nino Antigo)
    user = CustomUser.objects.get(id=8)
    print(f"👤 Testing with user: {user.first_name} {user.last_name} (ID: {user.id})")
    
    # Test the education list endpoint - this is what the frontend calls
    print(f"\n🔍 Testing GET /api/auth/education/ (what frontend calls)")
    
    # We need to simulate an authenticated request
    # Force login the user for testing
    client.force_login(user)
    
    # Test GET request to education endpoint
    response = client.get('/api/auth/education/')
    
    print(f"   Status Code: {response.status_code}")
    print(f"   Content-Type: {response.get('Content-Type', 'Not set')}")
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"   Response Data: {json.dumps(data, indent=2, default=str)}")
            print(f"   Number of records: {len(data) if isinstance(data, list) else 'Not a list'}")
        except json.JSONDecodeError:
            print(f"   Response Content (not JSON): {response.content.decode()}")
    else:
        print(f"   Error Response: {response.content.decode()}")
    
    # Test with another user who has education records (User 7 - Roman Osorio)
    print(f"\n🔍 Testing with User 7 (Roman Osorio) who has education records")
    try:
        user_7 = CustomUser.objects.get(id=7)
        client.force_login(user_7)
        
        response_7 = client.get('/api/auth/education/')
        print(f"   Status Code: {response_7.status_code}")
        
        if response_7.status_code == 200:
            try:
                data_7 = response_7.json()
                print(f"   Response Data: {json.dumps(data_7, indent=2, default=str)}")
                print(f"   Number of records: {len(data_7) if isinstance(data_7, list) else 'Not a list'}")
            except json.JSONDecodeError:
                print(f"   Response Content (not JSON): {response_7.content.decode()}")
        else:
            print(f"   Error Response: {response_7.content.decode()}")
            
    except CustomUser.DoesNotExist:
        print("   User 7 not found")
    
    # Test POST request (simulating form submission)
    print(f"\n🔍 Testing POST /api/auth/education/ (simulate form submission)")
    
    # Switch back to user 8
    client.force_login(user)
    
    test_education_data = {
        'institution': 'Test University',
        'degree_type': 'master',
        'field_of_study': 'Computer Science',
        'start_date': '2024-01-01',
        'end_date': '2025-12-31',
        'is_current': False
    }
    
    print(f"   Sending data: {json.dumps(test_education_data, indent=2)}")
    
    response_post = client.post('/api/auth/education/', 
                               data=json.dumps(test_education_data),
                               content_type='application/json')
    
    print(f"   Status Code: {response_post.status_code}")
    
    if response_post.status_code in [200, 201]:
        try:
            data_post = response_post.json()
            print(f"   Success Response: {json.dumps(data_post, indent=2, default=str)}")
            
            # Check if it was actually created
            new_count = Education.objects.filter(user=user).count()
            print(f"   Education records for user after POST: {new_count}")
            
            # Clean up test record
            if new_count > 0:
                Education.objects.filter(user=user).delete()
                print(f"   🧹 Cleaned up test records")
                
        except json.JSONDecodeError:
            print(f"   Response Content (not JSON): {response_post.content.decode()}")
    else:
        print(f"   Error Response: {response_post.content.decode()}")
        print(f"   Response Headers: {dict(response_post.items())}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== EDUCATION API TEST COMPLETE ===")