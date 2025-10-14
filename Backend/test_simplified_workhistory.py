"""
Test script to verify the simplified WorkHistory functionality works correctly.
Run this after starting the Django server.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser, WorkHistory
from auth_app.serializers import WorkHistorySerializer
from django.test import RequestFactory
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model

def test_simplified_work_history():
    """Test the simplified WorkHistory model and serializer"""
    
    print("🧪 Testing Simplified Work History Functionality")
    print("=" * 50)
    
    # Create or get a test user
    User = get_user_model()
    user, created = User.objects.get_or_create(
        username='testuser_experience',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User',
            'is_approved': True
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
        print(f"✅ Created test user: {user.username}")
    else:
        print(f"✅ Using existing test user: {user.username}")
    
    # Clear existing work history for clean test
    WorkHistory.objects.filter(user=user).delete()
    
    # Test 1: Create work history with simplified fields
    print("\n1️⃣ Testing WorkHistory creation with simplified fields...")
    
    work_data = {
        'occupation': 'Senior Software Developer',
        'employing_agency': 'Tech Innovations Inc.',
        'classification': 'private',
        'start_date': '2022-01-15',
        'end_date': '2023-12-31',
        'length_of_service': '2 years',
        'description': 'Led development team for web applications using Django and Vue.js. Implemented CI/CD pipelines and mentored junior developers.',
        'is_current_job': False
    }
    
    work_history = WorkHistory.objects.create(
        user=user,
        **work_data
    )
    
    print(f"✅ Created work history: {work_history}")
    print(f"   - Occupation: {work_history.occupation}")
    print(f"   - Company: {work_history.employing_agency}")
    print(f"   - Classification: {work_history.classification}")
    print(f"   - Current Job: {work_history.is_current_job}")
    print(f"   - Description: {work_history.description[:50]}...")
    
    # Test 2: Create current job
    print("\n2️⃣ Testing current job creation...")
    
    current_job_data = {
        'occupation': 'Lead Software Architect',
        'employing_agency': 'Future Tech Solutions',
        'classification': 'private',
        'start_date': '2024-01-01',
        'end_date': None,
        'length_of_service': '10 months',
        'description': 'Architect microservices solutions and lead multiple development teams. Focus on scalable cloud infrastructure.',
        'is_current_job': True
    }
    
    current_job = WorkHistory.objects.create(
        user=user,
        **current_job_data
    )
    
    print(f"✅ Created current job: {current_job}")
    print(f"   - Is Current: {current_job.is_current_job}")
    print(f"   - End Date: {current_job.end_date}")
    
    # Test 3: Test serializer
    print("\n3️⃣ Testing WorkHistorySerializer...")
    
    serializer = WorkHistorySerializer(work_history)
    serialized_data = serializer.data
    
    expected_fields = [
        'id', 'occupation', 'employing_agency', 'classification',
        'start_date', 'end_date', 'length_of_service', 'description',
        'is_current_job', 'skills'
    ]
    
    print("✅ Serializer fields present:")
    for field in expected_fields:
        if field in serialized_data:
            print(f"   ✓ {field}: {serialized_data[field]}")
        else:
            print(f"   ❌ Missing field: {field}")
    
    # Test 4: Test querying current job
    print("\n4️⃣ Testing current job query...")
    
    current_jobs = WorkHistory.objects.filter(user=user, is_current_job=True)
    print(f"✅ Found {current_jobs.count()} current job(s)")
    
    if current_jobs.exists():
        current = current_jobs.first()
        print(f"   - Current job: {current.occupation} at {current.employing_agency}")
    
    # Test 5: Test Profile model compatibility
    print("\n5️⃣ Testing Profile model compatibility...")
    
    from auth_app.models import Profile
    profile, created = Profile.objects.get_or_create(user=user)
    
    try:
        # This should trigger the save method that looks for current job
        profile.save()
        print("✅ Profile model updated successfully")
        print(f"   - Present occupation: {profile.present_occupation}")
        print(f"   - Employment classification: {profile.employment_classification}")
        print(f"   - Employing agency: {profile.employing_agency}")
    except Exception as e:
        print(f"❌ Profile model error: {e}")
    
    # Test 6: Test that removed fields are gone
    print("\n6️⃣ Verifying removed fields are not accessible...")
    
    removed_fields = [
        'job_type', 'employment_status', 'how_got_job', 
        'monthly_income', 'is_breadwinner', 'college_education_relevant'
    ]
    
    for field in removed_fields:
        if hasattr(WorkHistory, field):
            print(f"   ❌ Field {field} still exists in model")
        else:
            print(f"   ✅ Field {field} successfully removed")
    
    print("\n" + "=" * 50)
    print("🎉 Simplified Work History Test Complete!")
    print(f"📊 Total work histories for user: {WorkHistory.objects.filter(user=user).count()}")

if __name__ == "__main__":
    test_simplified_work_history()