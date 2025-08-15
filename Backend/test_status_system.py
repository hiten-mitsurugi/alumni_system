#!/usr/bin/env python
"""
Comprehensive test script for the online/offline status system.
Tests both database updates and WebSocket broadcasting.
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from auth_app.models import CustomUser, Profile
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def test_status_system():
    """Comprehensive test of the status system"""
    
    print("=" * 60)
    print("TESTING ONLINE/OFFLINE STATUS SYSTEM")
    print("=" * 60)
    
    # Get test users
    alumni_users = CustomUser.objects.filter(user_type=3, is_approved=True)[:3]
    if not alumni_users:
        print("❌ No approved alumni users found for testing")
        return
    
    print(f"📋 Found {len(alumni_users)} test users")
    
    # Test 1: Check current status of all users
    print("\n1️⃣ CURRENT USER STATUS:")
    print("-" * 40)
    for user in alumni_users:
        profile, created = Profile.objects.get_or_create(user=user)
        print(f"👤 {user.first_name} {user.last_name} (ID: {user.id})")
        print(f"   Status: {profile.status}")
        print(f"   Last Seen: {profile.last_seen}")
        if created:
            print(f"   ⚠️ Profile was just created")
        print()
    
    # Test 2: Simulate user going online
    print("2️⃣ SIMULATING USER LOGIN (going online):")
    print("-" * 40)
    test_user = alumni_users[0]
    profile, created = Profile.objects.get_or_create(user=test_user)
    
    old_status = profile.status
    profile.status = 'online'
    profile.last_seen = timezone.now()
    profile.save()
    
    print(f"👤 Updated {test_user.first_name} {test_user.last_name}:")
    print(f"   Status: {old_status} → {profile.status}")
    print(f"   Last Seen: {profile.last_seen}")
    
    # Test 3: Broadcast the status change
    print("\n3️⃣ BROADCASTING STATUS UPDATE:")
    print("-" * 40)
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            print("❌ No channel layer configured")
            return
            
        status_payload = {
            'type': 'status_update',
            'user_id': test_user.id,
            'status': 'online',
            'last_seen': profile.last_seen.isoformat()
        }
        
        print(f"📡 Broadcasting payload: {status_payload}")
        
        # Send to status_updates group (what NotificationConsumer listens to)
        async_to_sync(channel_layer.group_send)(
            'status_updates',
            status_payload
        )
        
        print("✅ Status update broadcast successful!")
        print("📱 Check your frontend console for received messages")
        
    except Exception as e:
        print(f"❌ Status broadcast failed: {str(e)}")
    
    # Test 4: Simulate user going offline
    print("\n4️⃣ SIMULATING USER LOGOUT (going offline):")
    print("-" * 40)
    
    profile.status = 'offline'
    profile.last_seen = timezone.now()
    profile.save()
    
    print(f"👤 Updated {test_user.first_name} {test_user.last_name}:")
    print(f"   Status: online → {profile.status}")
    print(f"   Last Seen: {profile.last_seen}")
    
    # Broadcast offline status
    try:
        status_payload = {
            'type': 'status_update',
            'user_id': test_user.id,
            'status': 'offline',
            'last_seen': profile.last_seen.isoformat()
        }
        
        print(f"📡 Broadcasting offline payload: {status_payload}")
        
        async_to_sync(channel_layer.group_send)(
            'status_updates',
            status_payload
        )
        
        print("✅ Offline status broadcast successful!")
        
    except Exception as e:
        print(f"❌ Offline broadcast failed: {str(e)}")
    
    # Test 5: Check final states
    print("\n5️⃣ FINAL STATUS CHECK:")
    print("-" * 40)
    for user in alumni_users:
        profile = Profile.objects.get(user=user)
        print(f"👤 {user.first_name} {user.last_name}: {profile.status} (last seen: {profile.last_seen})")
    
    print("\n" + "=" * 60)
    print("STATUS SYSTEM TEST COMPLETE")
    print("=" * 60)
    print("🔍 Check your frontend:")
    print("   1. Open browser console")
    print("   2. Look for status_update messages")
    print("   3. Check if status indicators change color")
    print("   4. Verify conversation list shows correct online/offline status")

if __name__ == "__main__":
    test_status_system()
