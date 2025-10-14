import requests
import json

# Test the simplified WorkHistory API
BASE_URL = 'http://localhost:8000'

def test_work_history_api():
    """Test the work history endpoints with simplified fields"""
    
    # First, let's try to login (you may need to adjust this for your auth setup)
    login_data = {
        'username': 'testuser',  # Replace with actual test user
        'password': 'testpass'   # Replace with actual test password
    }
    
    # Test data for creating work experience
    work_data = {
        'occupation': 'Software Developer',
        'employing_agency': 'Tech Company Inc.',
        'classification': 'private',
        'start_date': '2022-01-15',
        'end_date': '2023-12-31',
        'length_of_service': '2 years',
        'description': 'Developed web applications using Django and Vue.js. Led a team of 3 developers and implemented CI/CD pipelines.',
        'is_current_job': False
    }
    
    current_work_data = {
        'occupation': 'Senior Software Developer',
        'employing_agency': 'Another Tech Corp',
        'classification': 'private',
        'start_date': '2024-01-01',
        'end_date': None,  # Current job, no end date
        'length_of_service': '10 months',
        'description': 'Leading backend development team, architecting microservices solutions.',
        'is_current_job': True
    }
    
    print("Testing Work History API with simplified fields...")
    
    # Test creating work history
    print("\n1. Testing POST /api/auth/work-history/")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/work-history/",
            json=work_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ Work history created successfully")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Failed to create work history: {response.text}")
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed. Make sure the Django server is running on port 8000")
        return
    
    # Test creating current job
    print("\n2. Testing current job creation...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/work-history/",
            json=current_work_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 201]:
            print("✅ Current job created successfully")
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        else:
            print(f"❌ Failed to create current job: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test getting work history
    print("\n3. Testing GET /api/auth/work-history/")
    try:
        response = requests.get(f"{BASE_URL}/api/auth/work-history/")
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Work history retrieved successfully")
            data = response.json()
            print(f"Found {len(data) if isinstance(data, list) else 'N/A'} work experiences")
            if data:
                print("Sample work experience:")
                print(json.dumps(data[0] if isinstance(data, list) else data, indent=2))
        else:
            print(f"❌ Failed to get work history: {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_work_history_api()