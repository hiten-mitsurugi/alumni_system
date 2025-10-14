#!/usr/bin/env python
"""
Check what the enhanced profile API actually returns
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

from auth_app.models import CustomUser, Education, Profile
from auth_app.serializers import EnhancedUserDetailSerializer
import json

print("=== ENHANCED PROFILE API DATA CHECK ===")

try:
    # Get user 8 (Prince Nino Antigo)
    user = CustomUser.objects.get(id=8)
    print(f"👤 User: {user.first_name} {user.last_name}")
    
    print(f"\n🏫 CustomUser Education Data:")
    print(f"   program: {user.program}")
    print(f"   year_graduated: {user.year_graduated}")
    
    print(f"\n📋 Profile Education Data:")
    profile, created = Profile.objects.get_or_create(user=user)
    print(f"   program: {profile.program}")
    print(f"   year_graduated: {profile.year_graduated}")
    
    print(f"\n🎓 Education Table Records:")
    education_records = Education.objects.filter(user=user)
    print(f"   Count: {education_records.count()}")
    for edu in education_records:
        print(f"   - {edu.field_of_study} ({edu.degree_type}) at {edu.institution}")
    
    print(f"\n🔍 EnhancedUserDetailSerializer Output:")
    serializer = EnhancedUserDetailSerializer(user)
    data = serializer.data
    
    # Print the relevant fields
    print(f"   program: {data.get('program')}")
    print(f"   year_graduated: {data.get('year_graduated')}")
    print(f"   education (array): {data.get('education', [])}")
    print(f"   education count: {len(data.get('education', []))}")
    
    print(f"\n📊 Full API Response Structure:")
    print(f"   Keys: {list(data.keys())}")
    
    # Check if there are any nested education fields
    if 'profile' in data and data['profile']:
        profile_data = data['profile']
        print(f"\n📋 Profile nested data:")
        print(f"   profile.program: {profile_data.get('program')}")
        print(f"   profile.year_graduated: {profile_data.get('year_graduated')}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== API DATA CHECK COMPLETE ===")