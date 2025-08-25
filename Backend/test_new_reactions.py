#!/usr/bin/env python
"""
Test script for new LinkedIn-style reactions
"""
import os
import sys
import django
from django.conf import settings

# Add the Backend directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from posts_app.models import Post, Reaction
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
import json

def test_new_reactions():
    print("🧪 Testing New LinkedIn-Style Reactions...")
    
    # Get admin user
    User = get_user_model()
    try:
        admin_user = User.objects.get(email='admin@alumni.system')
        print(f"✅ Found admin user: {admin_user.email}")
    except User.DoesNotExist:
        print("❌ Admin user not found")
        return
    
    # Create API client with authentication
    client = APIClient()
    refresh = RefreshToken.for_user(admin_user)
    access_token = str(refresh.access_token)
    client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
    print(f"🔑 Using JWT token: {access_token[:50]}...")
    
    # Get the first post
    posts = Post.objects.filter(is_approved=True).first()
    if not posts:
        print("❌ No approved posts found")
        return
    
    post_id = posts.id
    print(f"📄 Testing reactions on post: {posts.title[:50]}...")
    
    # Test each new LinkedIn-style reaction
    new_reactions = ['like', 'applaud', 'sad', 'laugh', 'heart', 'support']
    
    for reaction_type in new_reactions:
        print(f"\n🎯 Testing {reaction_type} reaction...")
        
        # Add reaction
        response = client.post(f'/api/posts/posts/{post_id}/react/', {
            'reaction_type': reaction_type
        })
        
        if response.status_code == 201:
            print(f"✅ {reaction_type} reaction added successfully")
            reaction_data = response.json()
            print(f"   Emoji: {reaction_data.get('emoji', 'N/A')}")
        else:
            print(f"❌ Failed to add {reaction_type} reaction: {response.status_code}")
            print(f"   Response: {response.content.decode()}")
        
        # Remove reaction to test next one
        response = client.delete(f'/api/posts/posts/{post_id}/react/')
        if response.status_code == 204:
            print(f"✅ {reaction_type} reaction removed successfully")
        else:
            print(f"⚠️ Failed to remove {reaction_type} reaction")
    
    # Test getting post with reactions summary
    print(f"\n📊 Testing reactions summary...")
    response = client.get(f'/api/posts/posts/{post_id}/')
    if response.status_code == 200:
        post_data = response.json()
        reactions_summary = post_data.get('reactions_summary', [])
        print(f"✅ Reactions summary: {len(reactions_summary)} reaction types")
        for reaction in reactions_summary:
            if isinstance(reaction, dict):
                print(f"   {reaction.get('emoji', '?')} {reaction.get('type', 'unknown')}: {reaction.get('count', 0)}")
            else:
                print(f"   {reaction}")
    else:
        print(f"❌ Failed to get post details: {response.status_code}")
    
    # Check database directly
    print(f"\n🗄️ Database check:")
    all_reactions = Reaction.objects.all()
    print(f"Total reactions in DB: {all_reactions.count()}")
    
    reaction_counts = {}
    for reaction in all_reactions:
        reaction_type = reaction.reaction_type
        if reaction_type in reaction_counts:
            reaction_counts[reaction_type] += 1
        else:
            reaction_counts[reaction_type] = 1
    
    print("Reaction type distribution:")
    for reaction_type, count in reaction_counts.items():
        try:
            emoji = reaction.emoji  # This will use the model's emoji property
            print(f"   {emoji} {reaction_type}: {count}")
        except:
            print(f"   ❓ {reaction_type}: {count}")

if __name__ == '__main__':
    test_new_reactions()
