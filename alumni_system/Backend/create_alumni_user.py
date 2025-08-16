#!/usr/bin/env python
"""
Script to create an alumni user account with proper AlumniDirectory entry
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

def create_alumni_user():
    """Create an alumni user with proper directory entry"""
    
    # Alumni data
    alumni_data = {
        'email': 'alumni@alumni.com',
        'password': 'Alumni123!',
        'username': 'alumni_user',
        'first_name': 'John',
        'middle_name': 'Michael',
        'last_name': 'Smith',
        'school_id': '123-45678',
        'program': 'Bachelor of Science in Computer Science',
        'birth_date': date(1995, 5, 15),
        'year_graduated': 2020,
        'gender': 'male',
        'contact_number': '+1-234-567-8900',
        'address': '123 Alumni Street, Graduate City, State 12345',
        'civil_status': 'single',
        'employment_status': 'employed_locally'
    }
    
    try:
        # Step 1: Create or update AlumniDirectory entry
        print("Creating AlumniDirectory entry...")
        alumni_dir, created = AlumniDirectory.objects.get_or_create(
            school_id=alumni_data['school_id'],
            defaults={
                'first_name': alumni_data['first_name'],
                'middle_name': alumni_data['middle_name'],
                'last_name': alumni_data['last_name'],
                'birth_date': alumni_data['birth_date'],
                'program': alumni_data['program'],
                'year_graduated': alumni_data['year_graduated'],
                'gender': alumni_data['gender']
            }
        )
        
        if created:
            print(f"✅ AlumniDirectory entry created for {alumni_data['school_id']}")
        else:
            print(f"✅ AlumniDirectory entry already exists for {alumni_data['school_id']}")
        
        # Step 2: Delete existing user if exists
        CustomUser.objects.filter(email=alumni_data['email']).delete()
        print(f"🗑️  Removed existing user with email {alumni_data['email']}")
        
        # Step 3: Create the alumni user
        print("Creating alumni user...")
        user = CustomUser.objects.create(
            username=alumni_data['username'],
            email=alumni_data['email'],
            password=make_password(alumni_data['password']),
            first_name=alumni_data['first_name'],
            middle_name=alumni_data['middle_name'],
            last_name=alumni_data['last_name'],
            school_id=alumni_data['school_id'],
            program=alumni_data['program'],
            birth_date=alumni_data['birth_date'],
            year_graduated=alumni_data['year_graduated'],
            gender=alumni_data['gender'],
            contact_number=alumni_data['contact_number'],
            address=alumni_data['address'],
            civil_status=alumni_data['civil_status'],
            employment_status=alumni_data['employment_status'],
            user_type=3,  # Alumni
            is_staff=False,
            is_superuser=False,
            is_approved=True,  # Pre-approved for testing
            is_active=True
        )
        
        print("✅ Alumni user created successfully!")
        print(f"""
Alumni User Credentials:
========================
Email: {user.email}
Password: {alumni_data['password']}
Username: {user.username}
Name: {user.first_name} {user.middle_name} {user.last_name}
School ID: {user.school_id}
Program: {user.program}
Year Graduated: {user.year_graduated}
User Type: {user.get_user_type_display()}
Status: {'Approved' if user.is_approved else 'Pending Approval'}
""")

        # Step 4: Create additional alumni directory entries for variety
        print("\nCreating additional alumni directory entries for testing...")
        
        additional_alumni = [
            {
                'first_name': 'Jane',
                'middle_name': 'Elizabeth',
                'last_name': 'Doe',
                'school_id': '234-56789',
                'program': 'Bachelor of Science in Information Technology',
                'birth_date': date(1994, 8, 22),
                'year_graduated': 2019,
                'gender': 'female'
            },
            {
                'first_name': 'Robert',
                'middle_name': 'James',
                'last_name': 'Johnson',
                'school_id': '345-67890',
                'program': 'Bachelor of Arts in Business Administration',
                'birth_date': date(1993, 12, 10),
                'year_graduated': 2018,
                'gender': 'male'
            },
            {
                'first_name': 'Maria',
                'middle_name': 'Carmen',
                'last_name': 'Garcia',
                'school_id': '456-78901',
                'program': 'Bachelor of Science in Engineering',
                'birth_date': date(1996, 3, 5),
                'year_graduated': 2021,
                'gender': 'female'
            }
        ]
        
        for alumni in additional_alumni:
            alumni_entry, created = AlumniDirectory.objects.get_or_create(
                school_id=alumni['school_id'],
                defaults=alumni
            )
            if created:
                print(f"  ✅ Created directory entry for {alumni['first_name']} {alumni['last_name']} ({alumni['school_id']})")
            else:
                print(f"  ℹ️  Directory entry already exists for {alumni['school_id']}")
        
        print(f"\n🎉 Setup complete! You can now:")
        print(f"   1. Login with alumni credentials: {user.email} / {alumni_data['password']}")
        print(f"   2. Test registration with other alumni directory entries")
        print(f"   3. Use the alumni dashboard features")
        
    except Exception as e:
        print(f"❌ Error creating alumni user: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    create_alumni_user()
