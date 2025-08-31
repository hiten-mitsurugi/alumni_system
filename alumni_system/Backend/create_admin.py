#!/usr/bin/env python
"""
Script to create an admin account for the Alumni System
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

def create_admin_user():
    """Create an admin user"""
    
    # Admin details
    admin_email = 'admin@alumni.com'
    admin_password = 'Admin123!'
    
    # Delete existing admin user if exists
    existing_admin = CustomUser.objects.filter(email=admin_email).first()
    if existing_admin:
        existing_admin.delete()
        print(f"🗑️  Deleted existing admin user: {admin_email}")
    
    # Create admin user
    admin_user = CustomUser.objects.create(
        username='admin',
        email=admin_email,
        password=make_password(admin_password),
        first_name='Admin',
        last_name='User',
        user_type=2,  # 2 = Admin (not SuperAdmin)
        is_staff=True,
        is_superuser=False,  # Admin but not SuperAdmin
        is_approved=True,
        is_active=True,
        school_id='ADMIN-001',
        program='Administration',
        gender='prefer_not_to_say',
        year_graduated=2024
    )
    
    print("✅ Admin user created successfully!")
    print(f"""
Admin User Credentials:
======================
Email: {admin_user.email}
Password: {admin_password}
Username: {admin_user.username}
User Type: {admin_user.get_user_type_display()}
Permissions: Staff access (not SuperAdmin)

You can now login with these credentials to access admin features.
""")

if __name__ == '__main__':
    create_admin_user()
