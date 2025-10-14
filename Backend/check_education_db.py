#!/usr/bin/env python
"""
Check what's in the education table in the database
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

from auth_app.models import CustomUser, Education
import json
from django.utils import timezone

print("=== EDUCATION TABLE DATABASE CHECK ===")

try:
    # Get all education records
    all_education = Education.objects.all().order_by('user_id', 'created_at')
    print(f"📊 Total education records in database: {all_education.count()}")
    
    if all_education.count() > 0:
        print("\n📚 All Education Records:")
        print("-" * 80)
        
        for edu in all_education:
            user = edu.user
            print(f"ID: {edu.id}")
            print(f"User: {user.first_name} {user.last_name} (ID: {user.id}, Email: {user.email})")
            print(f"Institution: {edu.institution}")
            print(f"Degree Type: {edu.degree_type}")
            print(f"Field of Study: {edu.field_of_study}")
            print(f"Start Date: {edu.start_date}")
            print(f"End Date: {edu.end_date}")
            print(f"Is Current: {edu.is_current}")
            print(f"GPA: {edu.gpa}")
            print(f"Description: {edu.description}")
            print(f"Created: {edu.created_at}")
            print(f"Updated: {edu.updated_at}")
            print("-" * 80)
    else:
        print("\n❌ No education records found in database")
    
    # Check specifically for user ID 8 (Prince Nino Antigo)
    print(f"\n🔍 Education records for User ID 8 (Prince Nino Antigo):")
    user_8_education = Education.objects.filter(user_id=8).order_by('created_at')
    print(f"Count: {user_8_education.count()}")
    
    if user_8_education.exists():
        for edu in user_8_education:
            print(f"  - {edu.field_of_study} ({edu.degree_type}) at {edu.institution}")
            print(f"    Dates: {edu.start_date} to {edu.end_date} (Current: {edu.is_current})")
    else:
        print("  No education records found for this user")
    
    # Check user profile data for comparison
    print(f"\n👤 User Profile Data for comparison:")
    try:
        user = CustomUser.objects.get(id=8)
        print(f"Name: {user.first_name} {user.last_name}")
        print(f"Program: {user.program}")
        print(f"Year Graduated: {user.year_graduated}")
        print(f"Email: {user.email}")
    except CustomUser.DoesNotExist:
        print("User ID 8 not found")
    
    # Check all users with education records
    print(f"\n📈 Education records by user:")
    users_with_education = Education.objects.values_list('user_id', flat=True).distinct()
    for user_id in users_with_education:
        user = CustomUser.objects.get(id=user_id)
        count = Education.objects.filter(user_id=user_id).count()
        print(f"  User {user_id} ({user.first_name} {user.last_name}): {count} records")

except Exception as e:
    print(f"❌ Database error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== DATABASE CHECK COMPLETE ===")