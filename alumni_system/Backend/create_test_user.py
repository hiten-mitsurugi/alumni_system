#!/usr/bin/env python
"""
Simple script to create a test user for login
"""

import os
import django
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser
from django.contrib.auth.hashers import make_password

def create_test_user():
    """Create a simple test user"""
    
    # Delete existing test user if exists
    CustomUser.objects.filter(email='test@test.com').delete()
    
    # Create simple test user with complex password
    user = CustomUser.objects.create(
        username='testuser',
        email='test@test.com',
        password=make_password('Test123!'),
        first_name='Test',
        last_name='User',
        user_type=1,  # Super Admin
        is_staff=True,
        is_superuser=True,
        is_approved=True,
        is_active=True,
        school_id='TEST-001',
        program='Test Program'
    )
    
    print("✅ Test user created successfully!")
    print(f"""
Test User Credentials:
=====================
Email: {user.email}
Password: Test123!
Username: {user.username}
User Type: {user.get_user_type_display()}
""")

if __name__ == '__main__':
    create_test_user()
