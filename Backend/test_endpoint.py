#!/usr/bin/env python
import requests

# Test the API endpoint directly
base_url = 'http://localhost:8000'

# First, get a token by logging in
login_data = {
    'username': 'superadmin@alumni.system',
    'password': 'password'  # Default password - adjust if needed
}

try:
    # Login to get token
    print("=== LOGGING IN ===")
    login_response = requests.post(f'{base_url}/api/login/', json=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code == 200:
        token_data = login_response.json()
        token = token_data.get('access')
        print(f"Token obtained: {token[:20]}...")
        
        # Test the name resolution endpoint
        headers = {'Authorization': f'Bearer {token}'}
        
        test_names = ['romanosorio', 'mariagarcia', 'testadmin']
        
        print(f"\n=== TESTING NAME RESOLUTION ===")
        for name in test_names:
            url = f'{base_url}/api/alumni/by-name/{name}/'
            print(f"\nTesting: {url}")
            
            response = requests.get(url, headers=headers)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"Success: {response.json()}")
            else:
                print(f"Error: {response.text[:200]}...")
    
    else:
        print(f"Login failed: {login_response.text}")
        
except Exception as e:
    print(f"Error: {e}")
