import requests
import json

# Test posts API
login_data = {'email': 'admin@alumni.system', 'password': 'admin123'}
response = requests.post('http://localhost:8000/api/auth/login/', json=login_data)
token = response.json().get('access')

if token:
    headers = {'Authorization': f'Bearer {token}'}
    posts_response = requests.get('http://localhost:8000/api/posts/posts/', headers=headers)
    print(f'Posts API Status: {posts_response.status_code}')
    if posts_response.status_code == 200:
        posts_data = posts_response.json()
        print(f'Number of posts: {len(posts_data.get("results", []))}')
        for i, post in enumerate(posts_data.get('results', [])[:2]):
            print(f'Post {i+1}: {post.get("content", "No content")[:50]}...')
            print(f'  Media files: {len(post.get("media_files", []))}')
            print(f'  Author: {post.get("user", {}).get("full_name", "Unknown")}')
            print(f'  Created: {post.get("created_at", "Unknown")}')
            print()
    else:
        print(f'Error: {posts_response.text}')
else:
    print('Login failed')
