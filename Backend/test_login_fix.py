#!/usr/bin/env python
import requests
import json

# Test login endpoint
login_url = "http://localhost:8000/auth/login/"

# Test with a known user
test_data = {
    "email": "roman.osorio@carsu.edu.ph",
    "password": "Test123!"  # You'll need to use the actual password
}

try:
    response = requests.post(login_url, json=test_data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        print("✅ Login successful!")
        data = response.json()
        if 'access' in data:
            print(f"Access token received: {data['access'][:50]}...")
    else:
        print("❌ Login failed")
        
except Exception as e:
    print(f"Error: {e}")
