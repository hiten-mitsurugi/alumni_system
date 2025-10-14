#!/usr/bin/env python
"""
Test script to debug education API issues
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
from auth_app.serializers import EducationSerializer, EnhancedUserDetailSerializer
import json

print("=== EDUCATION API DEBUG TEST ===")

# Test with user ID 8 (from logs)
try:
    user = CustomUser.objects.get(id=8)
    print(f"✅ Found user: {user.first_name} {user.last_name} ({user.email})")
    print(f"   User program: {user.program}")
    print(f"   User year_graduated: {user.year_graduated}")
    
    # Check education records
    education_records = Education.objects.filter(user=user)
    print(f"\n📚 Education records for user {user.id}: {education_records.count()} found")
    
    for edu in education_records:
        print(f"   - {edu.field_of_study} at {edu.institution} ({edu.degree_type})")
        print(f"     Dates: {edu.start_date} to {edu.end_date}")
        print(f"     Current: {edu.is_current}")
    
    # Test serializer
    print(f"\n🔍 Testing EducationSerializer...")
    serializer = EducationSerializer(education_records, many=True)
    serialized_data = serializer.data
    print(f"   Serialized data: {json.dumps(serialized_data, indent=2, default=str)}")
    
    # Test enhanced serializer
    print(f"\n🔍 Testing EnhancedUserDetailSerializer...")
    enhanced_serializer = EnhancedUserDetailSerializer(user)
    enhanced_data = enhanced_serializer.data
    print(f"   Education in enhanced data: {json.dumps(enhanced_data.get('education', []), indent=2, default=str)}")
    
    # Test creating an education record
    print(f"\n📝 Testing education creation...")
    test_data = {
        'institution': 'Test University',
        'degree_type': 'master',
        'field_of_study': 'Computer Science',
        'start_date': '2024-01-01',
        'end_date': '2025-12-31',
        'is_current': False
    }
    
    create_serializer = EducationSerializer(data=test_data)
    if create_serializer.is_valid():
        # Don't actually save, just validate
        print(f"   ✅ Test data is valid: {create_serializer.validated_data}")
        
        # Test actual creation
        try:
            new_edu = create_serializer.save(user=user)
            print(f"   ✅ Created education record ID: {new_edu.id}")
            
            # Verify it was created
            count_after = Education.objects.filter(user=user).count()
            print(f"   📊 Education count after creation: {count_after}")
            
            # Clean up test record
            new_edu.delete()
            print(f"   🧹 Cleaned up test record")
            
        except Exception as create_error:
            print(f"   ❌ Error creating education: {create_error}")
            import traceback
            traceback.print_exc()
    else:
        print(f"   ❌ Test data is invalid: {create_serializer.errors}")

except CustomUser.DoesNotExist:
    print("❌ User with ID 8 not found")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== TEST COMPLETE ===")