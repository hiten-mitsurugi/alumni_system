#!/usr/bin/env python
"""
Test script to simulate frontend education creation request
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

from django.test import RequestFactory, Client
from django.contrib.auth import get_user_model
from auth_app.models import CustomUser
import json

print("=== FRONTEND EDUCATION POST TEST ===")

# Create a test client
client = Client()

# Get user
try:
    user = CustomUser.objects.get(id=8)
    print(f"✅ Testing with user: {user.first_name} {user.last_name}")
    
    # Login first to get JWT token (simulate frontend auth)
    login_data = {
        'email': user.email,
        'password': 'testpassword123'  # You might need the actual password
    }
    
    # Instead, let's manually create the request data like frontend sends
    education_data = {
        'institution': 'Harvard University',
        'degree_type': 'master',
        'field_of_study': 'Data Science',
        'start_date': '2024-09-01',
        'end_date': '2026-05-01',
        'is_current': False
    }
    
    print(f"🔍 Testing POST data: {json.dumps(education_data, indent=2)}")
    
    # Test the view directly
    from auth_app.views import EducationListCreateView
    from django.http import HttpRequest
    from rest_framework.test import APIRequestFactory, force_authenticate
    
    factory = APIRequestFactory()
    request = factory.post('/auth/education/', education_data, format='json')
    force_authenticate(request, user=user)
    
    view = EducationListCreateView()
    view.request = request
    
    # Test the serializer validation
    from auth_app.serializers import EducationSerializer
    serializer = EducationSerializer(data=education_data)
    
    if serializer.is_valid():
        print(f"✅ Data is valid: {serializer.validated_data}")
        
        # Try to save
        try:
            new_education = serializer.save(user=user)
            print(f"✅ Successfully created education ID: {new_education.id}")
            print(f"   Institution: {new_education.institution}")
            print(f"   Degree: {new_education.degree_type}")
            print(f"   Field: {new_education.field_of_study}")
            print(f"   Dates: {new_education.start_date} to {new_education.end_date}")
            
            # Verify it exists in database
            from auth_app.models import Education
            edu_count = Education.objects.filter(user=user).count()
            print(f"📊 Total education records for user: {edu_count}")
            
            # Clean up
            new_education.delete()
            print(f"🧹 Cleaned up test record")
            
        except Exception as save_error:
            print(f"❌ Error saving: {save_error}")
            import traceback
            traceback.print_exc()
    else:
        print(f"❌ Data validation failed: {serializer.errors}")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("\n=== FRONTEND POST TEST COMPLETE ===")