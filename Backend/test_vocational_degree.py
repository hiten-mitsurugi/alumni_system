#!/usr/bin/env python
"""
Test vocational degree type specifically
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

def test_vocational_degree():
    print("=== VOCATIONAL DEGREE TEST ===")
    
    try:
        # Get test user
        user = User.objects.get(id=8)  # Prince Nino Antigo
        print(f"👤 Testing with user: {user.first_name} {user.last_name} (ID: {user.id})")
        
        # Create authentication tokens
        refresh = RefreshToken.for_user(user)
        access_token = str(refresh.access_token)
        
        # Create API client
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        
        # Test data with vocational degree
        vocational_data = {
            "institution": "Technical Institute of Butuan",
            "degree_type": "vocational",
            "field_of_study": "Computer Hardware Servicing",
            "start_date": "2022-06-01",
            "end_date": "2023-03-31",
            "is_current": False
        }
        
        print(f"\n🔍 Testing POST with vocational degree:")
        print(f"Sending data: {vocational_data}")
        
        # Create vocational education
        response = client.post('/api/auth/education/', vocational_data, format='json')
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            print(f"✅ Success Response: {response.data}")
            education_id = response.data['id']
            
            # Test GET to verify it's saved correctly
            print(f"\n🔍 Testing GET after creation:")
            get_response = client.get('/api/auth/education/')
            print(f"Status Code: {get_response.status_code}")
            print(f"Response Data: {get_response.data}")
            
            # Clean up
            delete_response = client.delete(f'/api/auth/education/{education_id}/')
            print(f"\n🧹 Cleanup - Delete Status: {delete_response.status_code}")
            
        else:
            print(f"❌ Error: {response.data}")
            
    except User.DoesNotExist:
        print("❌ Test user with ID 8 not found")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n=== TEST COMPLETE ===")

if __name__ == "__main__":
    test_vocational_degree()