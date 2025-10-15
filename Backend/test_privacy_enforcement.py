#!/usr/bin/env python
"""
Test script to verify privacy enforcement is working correctly
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse
from auth_app.models import FieldPrivacySetting
import json

User = get_user_model()

def test_privacy_enforcement():
    """Test that privacy settings are properly enforced"""
    print("\n=== Testing Privacy Enforcement ===")
    
    # Clean up any existing test users
    User.objects.filter(username__in=['testuser1', 'testuser2']).delete()
    
    # Create test users
    user1 = User.objects.create_user(
        username='testuser1',
        email='test1@example.com',
        password='testpass123',
        first_name='John',
        last_name='Doe'
    )
    
    user2 = User.objects.create_user(
        username='testuser2', 
        email='test2@example.com',
        password='testpass123',
        first_name='Jane',
        last_name='Smith'
    )
    
    # Set user1's first_name to "Only for Me" privacy
    privacy_setting = FieldPrivacySetting.objects.create(
        user=user1,
        field_name='first_name',
        visibility='only_me'
    )
    
    print(f"Created privacy setting: {privacy_setting.field_name} = {privacy_setting.visibility}")
    
    # Test 1: User viewing their own profile (should see everything)
    client = Client()
    client.force_login(user1)
    
    response = client.get('/api/auth/profile/about-data/')
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.content}")
        return
        
    data = response.json()
    
    print(f"\n1. User1 viewing own profile:")
    print(f"   first_name visible: {data['field_data']['first_name']['is_visible']}")
    print(f"   first_name value: {data['field_data']['first_name']['value']}")
    
    # Test 2: Another user viewing user1's profile (should NOT see private fields)
    client.force_login(user2)
    
    response = client.get(f'/api/auth/profile/about-data/{user1.id}/')
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.content}")
        return
        
    data = response.json()
    
    print(f"\n2. User2 viewing User1's profile:")
    print(f"   first_name visible: {data['field_data']['first_name']['is_visible']}")
    
    # Test 3: Anonymous user viewing user1's profile (should be forbidden)
    client.logout()
    
    response = client.get(f'/api/auth/profile/about-data/{user1.id}/')
    
    print(f"\n3. Anonymous user viewing User1's profile:")
    if response.status_code == 403:
        print(f"   Status: {response.status_code} - Authentication required (CORRECT)")
    else:
        print(f"   Unexpected status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   first_name visible: {data['field_data']['first_name']['is_visible']}")
    
    # Test different privacy levels
    print(f"\n=== Testing Different Privacy Levels ===")
    
    # Set last_name to "For Connections"
    FieldPrivacySetting.objects.create(
        user=user1,
        field_name='last_name',
        visibility='connections_only'
    )
    
    # Set email to "For Everyone"
    FieldPrivacySetting.objects.create(
        user=user1,
        field_name='email',
        visibility='everyone'
    )
    
    # Test as another user (no connection)
    client.force_login(user2)
    response = client.get(f'/api/auth/profile/about-data/{user1.id}/')
    
    if response.status_code != 200:
        print(f"Error: {response.status_code} - {response.content}")
        return
        
    data = response.json()
    
    print(f"\n4. User2 viewing User1's profile (different privacy levels):")
    print(f"   first_name (only_me): {data['field_data']['first_name']['is_visible']}")
    print(f"   last_name (connections_only): {data['field_data']['last_name']['is_visible']}")
    print(f"   email (everyone): {data['field_data']['email']['is_visible']}")
    
    print(f"\n=== Privacy Test Complete ===")
    
    # Cleanup
    user1.delete()
    user2.delete()

if __name__ == '__main__':
    test_privacy_enforcement()