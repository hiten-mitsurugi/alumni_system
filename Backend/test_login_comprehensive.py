#!/usr/bin/env python
import requests
import json

# Test login endpoint with proper data
login_url = "http://localhost:8000/api/login/"

# Test with the known user data we found earlier
test_cases = [
    {
        "email": "roman.osorio@carsu.edu.ph",
        "password": "Test123!",  # You'll need to provide the actual password
        "description": "Roman Osorio login test"
    },
    {
        "email": "admin@test.com", 
        "password": "admin123",  # You'll need to provide the actual password
        "description": "Test admin login test"
    }
]

print("🔍 Testing Login Functionality")
print("=" * 50)

for i, test_data in enumerate(test_cases, 1):
    print(f"\n{i}. {test_data['description']}")
    print(f"   Email: {test_data['email']}")
    
    login_payload = {
        "email": test_data["email"],
        "password": test_data["password"]
    }
    
    try:
        print(f"   → Sending POST request to: {login_url}")
        response = requests.post(
            login_url, 
            json=login_payload,
            headers={'Content-Type': 'application/json'},
            timeout=10
        )
        
        print(f"   → Status Code: {response.status_code}")
        
        if response.status_code == 200:
            print("   ✅ Login successful!")
            data = response.json()
            if 'access' in data:
                print(f"   → Access token received: {data['access'][:50]}...")
            if 'refresh' in data:
                print(f"   → Refresh token received: {data['refresh'][:50]}...")
            if 'user' in data:
                user = data['user']
                print(f"   → User: {user.get('first_name', '')} {user.get('last_name', '')} (ID: {user.get('id', 'N/A')})")
        else:
            print(f"   ❌ Login failed")
            try:
                error_data = response.json()
                print(f"   → Error: {error_data}")
            except:
                print(f"   → Raw response: {response.text}")
                
    except requests.exceptions.ConnectionError:
        print("   ❌ Connection failed - Is the Django server running?")
    except requests.exceptions.Timeout:
        print("   ❌ Request timeout")
    except Exception as e:
        print(f"   ❌ Error: {e}")

print(f"\n" + "=" * 50)
print("Test completed!")
print("\n💡 If all tests failed with 'Invalid credentials':")
print("1. The passwords in this test might be wrong")
print("2. Please provide the correct passwords for these users")
print("3. Or check if there are other users you want to test with")
