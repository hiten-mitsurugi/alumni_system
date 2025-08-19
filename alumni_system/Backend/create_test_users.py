#!/usr/bin/env python
"""
Script to create test users for the Alumni System
Creates: superadmin, admin, and alumni users with specified credentials
"""

import os
import django
import sys
from datetime import date

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser, AlumniDirectory
from django.contrib.auth.hashers import make_password

def create_all_test_users():
    """Create all test users with specified credentials"""
    
    print("🚀 Creating test users for Alumni System...")
    print("=" * 50)
    
    # User data as specified
    users_data = [
        {
            'email': 'test@test.com',
            'password': 'Test123!',
            'username': 'superadmin',
            'first_name': 'Super',
            'middle_name': 'Test',
            'last_name': 'Admin',
            'user_type': 1,  # Super Admin
            'is_staff': True,
            'is_superuser': True,
            'school_id': 'SUPER-001',
            'program': 'System Administration'
        },
        {
            'email': 'admin@alumni.com',
            'password': 'Admin123!',
            'username': 'admin',
            'first_name': 'Test',
            'middle_name': 'Admin',
            'last_name': 'User',
            'user_type': 2,  # Admin
            'is_staff': True,
            'is_superuser': False,
            'school_id': 'ADMIN-001',
            'program': 'Administration'
        },
        {
            'email': 'alumni@alumni.com',
            'password': 'Alumni123!',
            'username': 'alumni_user',
            'first_name': 'Test',
            'middle_name': 'Alumni',
            'last_name': 'User',
            'user_type': 3,  # Alumni
            'is_staff': False,
            'is_superuser': False,
            'school_id': '123-45678',
            'program': 'Bachelor of Science in Computer Science',
            'birth_date': date(1995, 5, 15),
            'year_graduated': 2020,
            'contact_number': '+1-234-567-8900',
            'address': '123 Test Street, Test City, State 12345',
            'civil_status': 'single',
            'employment_status': 'employed_locally'
        }
    ]
    
    created_users = []
    
    for user_data in users_data:
        try:
            # Delete existing user if exists
            existing_user = CustomUser.objects.filter(email=user_data['email']).first()
            if existing_user:
                existing_user.delete()
                print(f"🗑️  Deleted existing user: {user_data['email']}")
            
            # For alumni users, create directory entry first
            if user_data['user_type'] == 3:  # Alumni
                print(f"Creating AlumniDirectory entry for {user_data['school_id']}...")
                alumni_dir, created = AlumniDirectory.objects.get_or_create(
                    school_id=user_data['school_id'],
                    defaults={
                        'first_name': user_data['first_name'],
                        'middle_name': user_data['middle_name'],
                        'last_name': user_data['last_name'],
                        'birth_date': user_data['birth_date'],
                        'program': user_data['program'],
                        'year_graduated': user_data['year_graduated'],
                        'gender': 'prefer_not_to_say'
                    }
                )
            
            # Create the user
            user = CustomUser.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                password=make_password(user_data['password']),
                first_name=user_data['first_name'],
                middle_name=user_data['middle_name'],
                last_name=user_data['last_name'],
                school_id=user_data['school_id'],
                program=user_data['program'],
                user_type=user_data['user_type'],
                is_staff=user_data['is_staff'],
                is_superuser=user_data['is_superuser'],
                is_approved=True,
                is_active=True,
                gender='prefer_not_to_say',
                birth_date=user_data.get('birth_date', date(1990, 1, 1)),
                year_graduated=user_data.get('year_graduated', 2020),
                contact_number=user_data.get('contact_number', ''),
                address=user_data.get('address', ''),
                civil_status=user_data.get('civil_status', 'single'),
                employment_status=user_data.get('employment_status', 'unemployed')
            )
            
            created_users.append({
                'user': user,
                'password': user_data['password']
            })
            
            user_type_name = user.get_user_type_display()
            print(f"✅ {user_type_name} created: {user.email}")
            
        except Exception as e:
            print(f"❌ Error creating user {user_data['email']}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    # Display summary
    print("\n" + "=" * 50)
    print("🎉 USER CREATION SUMMARY")
    print("=" * 50)
    
    for user_info in created_users:
        user = user_info['user']
        password = user_info['password']
        print(f"""
{user.get_user_type_display().upper()} CREDENTIALS:
Email: {user.email}
Password: {password}
Username: {user.username}
Name: {user.first_name} {user.middle_name} {user.last_name}
School ID: {user.school_id}
Permissions: {'Superuser' if user.is_superuser else 'Staff' if user.is_staff else 'Regular User'}
Status: {'✅ Active & Approved' if user.is_approved else '⏳ Pending Approval'}
""")
    
    print("🚀 All users created successfully!")
    print("You can now login with any of these credentials.")

if __name__ == '__main__':
    create_all_test_users()
