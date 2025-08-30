#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

# Get a test user to authenticate with
test_user = User.objects.filter(is_approved=True, is_active=True).first()
print(f"Test user: {test_user.username}")

# Create API client and authenticate
client = APIClient()
refresh = RefreshToken.for_user(test_user)
client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')

# Test the API endpoint
test_names = ['romanosorio', 'mariagarcia', 'testadmin']

print("=== TESTING API ENDPOINTS ===")
for name in test_names:
    print(f"\nTesting: /api/auth/alumni/by-name/{name}/")
    response = client.get(f'/api/auth/alumni/by-name/{name}/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Data: {response.data}")
    else:
        print(f"Error: {response.data if hasattr(response, 'data') else response.content}")
