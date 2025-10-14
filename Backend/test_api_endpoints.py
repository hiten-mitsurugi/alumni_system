"""
Test the WorkHistory API endpoints with the simplified fields.
This tests the actual REST API endpoints.
"""
import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token
import json

def test_work_history_api_endpoints():
    """Test the WorkHistory API endpoints"""
    
    print("🌐 Testing Work History API Endpoints")
    print("=" * 50)
    
    # Create test client
    client = Client()
    User = get_user_model()
    
    # Get or create test user
    user, created = User.objects.get_or_create(
        username='api_test_user',
        defaults={
            'email': 'apitest@example.com',
            'first_name': 'API',
            'last_name': 'Test',
            'is_approved': True
        }
    )
    
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Login user
    login_success = client.login(username='api_test_user', password='testpass123')
    print(f"✅ User login: {'Success' if login_success else 'Failed'}")
    
    if not login_success:
        print("❌ Could not log in user. API tests skipped.")
        return
    
    # Test 1: POST - Create work history
    print("\n1️⃣ Testing POST /api/auth/work-history/")
    
    work_data = {
        'occupation': 'Full Stack Developer',
        'employing_agency': 'Digital Solutions Ltd.',
        'classification': 'private',
        'start_date': '2023-03-01',
        'end_date': '2024-02-29',
        'length_of_service': '1 year',
        'description': 'Developed responsive web applications using React and Django REST framework. Managed database optimization and API development.',
        'is_current_job': False
    }
    
    response = client.post(
        '/api/auth/work-history/',
        data=json.dumps(work_data),
        content_type='application/json'
    )
    
    print(f"   Status Code: {response.status_code}")
    if response.status_code in [200, 201]:
        response_data = response.json()
        print("   ✅ Work history created successfully")
        print(f"   📝 Created ID: {response_data.get('id')}")
        work_id = response_data.get('id')
    else:
        print(f"   ❌ Failed to create work history")
        print(f"   Response: {response.content.decode()}")
        return
    
    # Test 2: POST - Create current job
    print("\n2️⃣ Testing POST current job...")
    
    current_job_data = {
        'occupation': 'Senior Full Stack Developer',
        'employing_agency': 'Innovation Tech Corp',
        'classification': 'private',
        'start_date': '2024-03-01',
        'end_date': None,
        'length_of_service': '7 months',
        'description': 'Leading frontend development initiatives. Implementing modern React patterns and optimizing application performance.',
        'is_current_job': True
    }
    
    response = client.post(
        '/api/auth/work-history/',
        data=json.dumps(current_job_data),
        content_type='application/json'
    )
    
    print(f"   Status Code: {response.status_code}")
    if response.status_code in [200, 201]:
        current_job_response = response.json()
        print("   ✅ Current job created successfully")
        print(f"   📝 Current job end date: {current_job_response.get('end_date')}")
        current_job_id = current_job_response.get('id')
    else:
        print(f"   ❌ Failed to create current job")
        print(f"   Response: {response.content.decode()}")
        return
    
    # Test 3: GET - List work histories
    print("\n3️⃣ Testing GET /api/auth/work-history/")
    
    response = client.get('/api/auth/work-history/')
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 200:
        work_histories = response.json()
        print(f"   ✅ Retrieved {len(work_histories)} work histories")
        
        for work in work_histories:
            print(f"   📋 {work['occupation']} at {work['employing_agency']}")
            print(f"      Current: {work['is_current_job']}")
            print(f"      Classification: {work['classification']}")
    else:
        print(f"   ❌ Failed to retrieve work histories")
        print(f"   Response: {response.content.decode()}")
    
    # Test 4: PUT - Update work history
    print("\n4️⃣ Testing PUT /api/auth/work-history/{id}/")
    
    updated_data = {
        'occupation': 'Senior Full Stack Developer (Updated)',
        'employing_agency': 'Digital Solutions Ltd.',
        'classification': 'private',
        'start_date': '2023-03-01',
        'end_date': '2024-02-29',
        'length_of_service': '11 months',
        'description': 'Updated description: Led cross-functional teams and implemented scalable microservices architecture.',
        'is_current_job': False
    }
    
    response = client.put(
        f'/api/auth/work-history/{work_id}/',
        data=json.dumps(updated_data),
        content_type='application/json'
    )
    
    print(f"   Status Code: {response.status_code}")
    if response.status_code == 200:
        updated_work = response.json()
        print("   ✅ Work history updated successfully")
        print(f"   📝 Updated occupation: {updated_work.get('occupation')}")
        print(f"   📝 Updated length: {updated_work.get('length_of_service')}")
    else:
        print(f"   ❌ Failed to update work history")
        print(f"   Response: {response.content.decode()}")
    
    # Test 5: DELETE - Delete work history
    print("\n5️⃣ Testing DELETE /api/auth/work-history/{id}/")
    
    response = client.delete(f'/api/auth/work-history/{work_id}/')
    print(f"   Status Code: {response.status_code}")
    
    if response.status_code == 204:
        print("   ✅ Work history deleted successfully")
    else:
        print(f"   ❌ Failed to delete work history")
        print(f"   Response: {response.content.decode()}")
    
    # Test 6: Verify simplified fields only
    print("\n6️⃣ Verifying only simplified fields are returned...")
    
    response = client.get('/api/auth/work-history/')
    if response.status_code == 200:
        work_histories = response.json()
        if work_histories:
            work = work_histories[0]
            
            # Check for expected fields
            expected_fields = [
                'id', 'occupation', 'employing_agency', 'classification',
                'start_date', 'end_date', 'length_of_service', 'description',
                'is_current_job', 'skills'
            ]
            
            # Check for removed fields (these should NOT be present)
            removed_fields = [
                'job_type', 'employment_status', 'how_got_job',
                'monthly_income', 'is_breadwinner', 'college_education_relevant'
            ]
            
            print("   ✅ Expected fields present:")
            for field in expected_fields:
                if field in work:
                    print(f"      ✓ {field}")
                else:
                    print(f"      ❌ Missing: {field}")
            
            print("   ✅ Removed fields not present:")
            for field in removed_fields:
                if field not in work:
                    print(f"      ✓ {field} (correctly removed)")
                else:
                    print(f"      ❌ {field} (still present!)")
    
    print("\n" + "=" * 50)
    print("🎉 API Endpoint Tests Complete!")

if __name__ == "__main__":
    test_work_history_api_endpoints()