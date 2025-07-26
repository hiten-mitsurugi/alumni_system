#!/usr/bin/env python
"""
Script to create a superadmin user for the Alumni System
Run this script with: python create_superadmin.py
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

def create_superadmin():
    """Create or update the superadmin user"""
    
    # Check if superadmin already exists
    try:
        superadmin = CustomUser.objects.get(username='johnantigo')
        print("Superadmin user already exists. Updating...")
        
        # Update existing user
        superadmin.email = 'johnantigo@example.com'
        superadmin.password = make_password('!John2004')
        superadmin.first_name = 'John'
        superadmin.middle_name = 'Diaz'
        superadmin.last_name = 'Antigo'
        superadmin.user_type = 1  # Super Admin
        superadmin.is_staff = True
        superadmin.is_superuser = True
        superadmin.is_approved = True
        superadmin.gender = 'male'
        superadmin.school_id = 'SUPER-001'  # Unique school ID for superadmin
        superadmin.program = 'System Administration'
        
        superadmin.save()
        print("✅ Superadmin user updated successfully!")
        
    except CustomUser.DoesNotExist:
        print("Creating new superadmin user...")
        
        # Create new superadmin user
        superadmin = CustomUser.objects.create(
            username='johnantigo',
            email='johnantigo@example.com',
            password=make_password('!John2004'),
            first_name='John',
            middle_name='Diaz',
            last_name='Antigo',
            user_type=1,  # Super Admin
            is_staff=True,
            is_superuser=True,
            is_approved=True,
            gender='male',
            school_id='SUPER-001',  # Unique school ID for superadmin
            program='System Administration'
        )
        
        print("✅ Superadmin user created successfully!")
    
    print(f"""
Superadmin Credentials:
======================
Username: {superadmin.username}
Email: {superadmin.email}
Password: !John2004
User Type: {superadmin.get_user_type_display()}
School ID: {superadmin.school_id}
""")

if __name__ == '__main__':
    create_superadmin()
