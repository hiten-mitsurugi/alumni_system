#!/usr/bin/env python
"""
Quick test script to verify the posts API is working
"""
import os
import django
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from posts_app.models import Post, PostMedia
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json

User = get_user_model()

def test_posts_api():
    print("🧪 Testing Posts API...")
    
    # Get or create admin user
    try:
        admin_user = User.objects.get(email='admin@alumni.system')
        print(f"✅ Found admin user: {admin_user.email}")
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return
    
    # Create API client
    client = APIClient()
    
    # Get JWT token
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)
    
    # Set authorization header
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    
    print(f"🔑 Using JWT token: {access_token[:20]}...")
    
    # Test GET posts endpoint
    print("\n📡 Testing GET /api/posts/posts/")
    response = client.get('/api/posts/posts/')
    print(f"Response status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Posts API working! Found {len(data.get('results', data))} posts")
        
        # Print first post if any
        posts = data.get('results', data)
        if posts:
            first_post = posts[0]
            print(f"First post: {first_post.get('title', 'No title')} by {first_post.get('user', {}).get('first_name', 'Unknown')}")
        else:
            print("📝 No posts found - creating a test post...")
            
            # Create a test post
            test_response = client.post('/api/posts/posts/create/', {
                'title': 'Test Post from API',
                'content': 'This is a test post created via API to verify the system is working!',
                'content_category': 'general',
                'visibility': 'public'
            })
            
            print(f"Create post response: {test_response.status_code}")
            if test_response.status_code == 201:
                print("✅ Test post created successfully!")
                created_post = test_response.json()
                print(f"Created post ID: {created_post.get('id')}")
            else:
                print(f"❌ Failed to create test post: {test_response.content}")
    else:
        print(f"❌ Posts API failed: {response.status_code}")
        print(f"Error: {response.content}")
    
    # Check database directly
    print(f"\n📊 Database check:")
    total_posts = Post.objects.count()
    approved_posts = Post.objects.filter(is_approved=True).count()
    print(f"Total posts in DB: {total_posts}")
    print(f"Approved posts: {approved_posts}")
    
    # Check media files
    total_media = PostMedia.objects.count()
    print(f"Total media files: {total_media}")

if __name__ == '__main__':
    test_posts_api()
