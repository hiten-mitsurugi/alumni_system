#!/usr/bin/env python3
"""
Debug script to test status system step by step
"""

import os
import django
import asyncio
from channels.layers import get_channel_layer

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from auth_app.models import Profile
from django.utils import timezone
from asgiref.sync import async_to_sync
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

User = get_user_model()

def test_user_profiles():
    """Test that users have profiles with status fields"""
    print("=== Testing User Profiles ===")
    
    users = User.objects.all()[:5]  # Get first 5 users
    
    for user in users:
        profile, created = Profile.objects.get_or_create(user=user)
        print(f"User {user.id} ({user.first_name} {user.last_name}):")
        print(f"  - Profile exists: {not created}")
        print(f"  - Current status: {profile.status}")
        print(f"  - Last seen: {profile.last_seen}")
        print()

def test_status_update():
    """Test updating a user's status"""
    print("=== Testing Status Update ===")
    
    # Get first user
    user = User.objects.first()
    if not user:
        print("No users found!")
        return
        
    profile, created = Profile.objects.get_or_create(user=user)
    
    print(f"Testing with user {user.id} ({user.first_name} {user.last_name})")
    print(f"Before: status={profile.status}, last_seen={profile.last_seen}")
    
    # Update status to online
    profile.status = 'online'
    profile.last_seen = timezone.now()
    profile.save()
    
    print(f"After: status={profile.status}, last_seen={profile.last_seen}")

def test_status_broadcast():
    """Test broadcasting status update"""
    print("=== Testing Status Broadcast ===")
    
    user = User.objects.first()
    if not user:
        print("No users found!")
        return
        
    profile, created = Profile.objects.get_or_create(user=user)
    profile.status = 'online'
    profile.last_seen = timezone.now()
    profile.save()
    
    # Broadcast status change
    channel_layer = get_channel_layer()
    status_payload = {
        'type': 'status_update',
        'user_id': user.id,
        'status': 'online',
        'last_seen': profile.last_seen.isoformat()
    }
    
    print(f"Broadcasting payload: {status_payload}")
    
    try:
        async_to_sync(channel_layer.group_send)(
            'status_updates',
            status_payload
        )
        print("✅ Status broadcast sent successfully!")
    except Exception as e:
        print(f"❌ Status broadcast failed: {e}")

def test_frontend_timing_logic():
    """Test the frontend timing logic for determining online status"""
    print("=== Testing Frontend Timing Logic ===")
    
    # Simulate the frontend logic
    from datetime import datetime, timedelta
    
    now = timezone.now()
    
    # Test cases
    test_cases = [
        ("Just logged in", now, 'online'),
        ("1 minute ago, online", now - timedelta(minutes=1), 'online'),
        ("3 minutes ago, online", now - timedelta(minutes=3), 'online'),
        ("1 minute ago, offline", now - timedelta(minutes=1), 'offline'),
        ("10 minutes ago, online", now - timedelta(minutes=10), 'online'),
    ]
    
    for description, last_seen, status in test_cases:
        diff_minutes = (now - last_seen).total_seconds() / 60
        is_recent = diff_minutes <= 2
        is_online_status = status == 'online'
        result = is_recent and is_online_status
        
        print(f"{description}:")
        print(f"  - Last seen: {last_seen}")
        print(f"  - Status: {status}")
        print(f"  - Minutes ago: {diff_minutes:.1f}")
        print(f"  - Is recent (≤2 min): {is_recent}")
        print(f"  - Is online status: {is_online_status}")
        print(f"  - Should show online: {result}")
        print()

if __name__ == "__main__":
    print("🔍 STATUS SYSTEM DEBUG")
    print("=" * 50)
    
    test_user_profiles()
    test_status_update()
    test_status_broadcast()
    test_frontend_timing_logic()
    
    print("=" * 50)
    print("Debug completed!")
