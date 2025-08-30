#!/usr/bin/env python
import requests
import json

# Test login endpoint with REAL credentials
login_url = "http://localhost:8000/api/login/"

# Real user credentials provided by user
test_data = {
    "email": "osorioroman101@gmail.com",
    "password": "iloveyouLord143!",
    "description": "Real user login test"
}

print("🔍 Testing Login with Real Credentials")
print("=" * 50)
print(f"Email: {test_data['email']}")
print(f"Testing URL: {login_url}")

login_payload = {
    "email": test_data["email"],
    "password": test_data["password"]
}

try:
    print(f"\n→ Sending POST request...")
    response = requests.post(
        login_url, 
        json=login_payload,
        headers={'Content-Type': 'application/json'},
        timeout=10
    )
    
    print(f"→ Status Code: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ LOGIN SUCCESSFUL!")
        data = response.json()
        
        print("\n📄 Response Data:")
        if 'access' in data:
            print(f"  → Access Token: {data['access'][:50]}...")
        if 'refresh' in data:
            print(f"  → Refresh Token: {data['refresh'][:50]}...")
        if 'user' in data:
            user = data['user']
            print(f"  → User ID: {user.get('id', 'N/A')}")
            print(f"  → Name: {user.get('first_name', '')} {user.get('last_name', '')}")
            print(f"  → Username: {user.get('username', 'N/A')}")
            print(f"  → Email: {user.get('email', 'N/A')}")
            print(f"  → User Type: {user.get('user_type', 'N/A')}")
            print(f"  → Approved: {user.get('is_approved', 'N/A')}")
        
    elif response.status_code == 401:
        print("❌ LOGIN FAILED - Invalid Credentials")
        try:
            error_data = response.json()
            print(f"  → Error: {error_data}")
        except:
            print(f"  → Raw response: {response.text}")
    elif response.status_code == 403:
        print("❌ LOGIN FAILED - Account Not Approved or Blocked")
        try:
            error_data = response.json()
            print(f"  → Error: {error_data}")
        except:
            print(f"  → Raw response: {response.text}")
    else:
        print(f"❌ LOGIN FAILED - Unexpected Status Code")
        try:
            error_data = response.json()
            print(f"  → Error: {error_data}")
        except:
            print(f"  → Raw response: {response.text}")
            
except requests.exceptions.ConnectionError:
    print("❌ Connection failed - Is the Django server running on localhost:8000?")
except requests.exceptions.Timeout:
    print("❌ Request timeout")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print(f"\n" + "=" * 50)
print("Test completed!")
