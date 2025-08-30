#!/usr/bin/env python
import requests

# Test the API endpoint directly
url = "http://localhost:8000/api/alumni/by-name/romanosorio/"

# You'll need to get a valid token first
# For now, let's just test if the endpoint responds
try:
    # Try without auth first to see if it's a routing issue
    response = requests.get(url)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
