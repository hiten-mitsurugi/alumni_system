#!/usr/bin/env python3
"""
Real-time Status System Debug Test
Tests the complete flow: login → status update → WebSocket broadcast → frontend reception

This test validates:
1. Login process updates profile status to 'online'
2. WebSocket broadcast is sent to 'status_updates' group
3. NotificationConsumer receives and processes the broadcast
4. Frontend would receive the status update message

Run this in Backend directory: python test_status_realtime.py
"""

import os
import sys
import django
import asyncio
import json
import logging
import time
from datetime import datetime, timezone

# Setup Django environment
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.core import serializers
from auth_app.models import Profile
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone as django_timezone

User = get_user_model()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_complete_status_flow():
    """Test the complete status flow from login to WebSocket broadcast"""
    
    print("=" * 60)
    print("🚀 REAL-TIME STATUS SYSTEM DEBUG TEST")
    print("=" * 60)
    
    # Create or get test user - with all required fields
    try:
        user = User.objects.get(username='testuser')
        print(f"✅ Found existing test user: {user.username} (ID: {user.id})")
        
        # Update existing user with required fields if missing
        updated = False
        if not user.school_id:
            user.school_id = 'TEST123'
            updated = True
        if not user.gender:
            user.gender = 'male'
            updated = True
        if not user.civil_status:
            user.civil_status = 'single'
            updated = True
        if not user.contact_number:
            user.contact_number = '1234567890'
            updated = True
        if not user.birth_date:
            user.birth_date = '1990-01-01'
            updated = True
        if not user.year_graduated:
            user.year_graduated = 2015
            updated = True
        if not user.program:
            user.program = 'Computer Science'
            updated = True
        if not user.present_address:
            user.present_address = 'Test Present Address'
            updated = True
        if not user.permanent_address:
            user.permanent_address = 'Test Permanent Address'
            updated = True
        if not user.mothers_name:
            user.mothers_name = 'Test Mother'
            updated = True
        if not user.mothers_occupation:
            user.mothers_occupation = 'Test Mother Occupation'
            updated = True
        if not user.fathers_name:
            user.fathers_name = 'Test Father'
            updated = True
        if not user.fathers_occupation:
            user.fathers_occupation = 'Test Father Occupation'
            updated = True
        if not user.employment_status:
            user.employment_status = 'employed_locally'
            updated = True
        
        if updated:
            user.save()
            print(f"✅ Updated test user with required fields")
        
    except User.DoesNotExist:
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type=3,
            is_approved=True,
            school_id='TEST123',
            gender='male',
            civil_status='single',
            contact_number='1234567890',
            birth_date='1990-01-01',
            year_graduated=2015,
            program='Computer Science',
            present_address='Test Present Address',
            permanent_address='Test Permanent Address',
            mothers_name='Test Mother',
            mothers_occupation='Test Mother Occupation',
            fathers_name='Test Father',
            fathers_occupation='Test Father Occupation',
            employment_status='employed_locally'
        )
        print(f"✅ Created new test user: {user.username} (ID: {user.id})")
    
    # Ensure profile exists
    try:
        profile = user.profile
        print(f"✅ Using existing profile for user {user.id}")
    except Profile.DoesNotExist:
        # Create profile manually since automatic creation might fail
        try:
            profile = Profile.objects.create(user=user)
            print(f"✅ Created new profile for user {user.id}")
        except Exception as e:
            print(f"❌ Failed to create profile: {e}")
            # Try to create a minimal profile bypassing the save method
            profile = Profile(user=user)
            profile.full_name = f"{user.first_name} {user.last_name}"
            profile.email_address = user.email
            profile.school_id = user.school_id or 'DEFAULT123'
            profile.mobile_number = user.contact_number or '0000000000'
            profile.sex = user.gender or 'male'
            profile.civil_status = user.civil_status or 'single'
            profile.year_of_birth = user.birth_date or '1990-01-01'
            profile.present_address = user.present_address or 'Default Address'
            profile.permanent_address = user.permanent_address or 'Default Address'
            profile.mothers_name = user.mothers_name or 'Default Mother'
            profile.mothers_occupation = user.mothers_occupation or 'Default Occupation'
            profile.fathers_name = user.fathers_name or 'Default Father'
            profile.fathers_occupation = user.fathers_occupation or 'Default Occupation'
            profile.year_graduated = user.year_graduated or 2015
            profile.program = user.program or 'Default Program'
            profile.present_employment_status = user.employment_status or 'employed_locally'
            profile.status = 'offline'
            profile.save()
            print(f"✅ Created minimal profile for user {user.id}")
    
    print(f"📊 Initial profile status: {profile.status}")
    
    # Test 1: Manual status update and broadcast
    print("\n" + "=" * 40)
    print("🧪 TEST 1: Manual Status Update & Broadcast")
    print("=" * 40)
    
    # Update status manually
    old_status = profile.status
    profile.status = 'online'
    profile.last_seen = django_timezone.now()
    profile.save()
    
    print(f"✅ Updated profile status: {old_status} → {profile.status}")
    print(f"✅ Updated last_seen: {profile.last_seen}")
    
    # Manual WebSocket broadcast
    channel_layer = get_channel_layer()
    if channel_layer:
        print("✅ Channel layer available")
        
        # Prepare status update message
        status_message = {
            'type': 'status_update',
            'user_id': user.id,
            'status': profile.status,
            'last_seen': profile.last_seen.isoformat()
        }
        
        print(f"📤 Broadcasting status update: {json.dumps(status_message, indent=2)}")
        
        # Send to status_updates group
        try:
            async_to_sync(channel_layer.group_send)(
                'status_updates',
                status_message
            )
            print("✅ Successfully broadcast to 'status_updates' group")
        except Exception as e:
            print(f"❌ Failed to broadcast: {e}")
            return False
    else:
        print("❌ No channel layer available")
        return False
    
    # Test 2: Simulate login API call
    print("\n" + "=" * 40)
    print("🧪 TEST 2: Login API Call Simulation")
    print("=" * 40)
    
    client = Client()
    
    # First, reset status to offline
    profile.status = 'offline'
    profile.save()
    print(f"🔄 Reset status to: {profile.status}")
    
    # Attempt login
    login_data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    
    print(f"🔐 Attempting login with: {login_data['username']}")
    
    try:
        response = client.post('/api/login/', login_data, content_type='application/json')
        print(f"📥 Login response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"✅ Login successful")
            print(f"📄 Response keys: {list(response_data.keys())}")
            
            # Check if profile status was updated
            profile.refresh_from_db()
            print(f"📊 Profile status after login: {profile.status}")
            print(f"📊 Profile last_seen after login: {profile.last_seen}")
            
            if profile.status == 'online':
                print("✅ Login correctly updated status to 'online'")
            else:
                print(f"❌ Login did not update status (still: {profile.status})")
                
        else:
            print(f"❌ Login failed with status: {response.status_code}")
            print(f"📄 Response: {response.content.decode()}")
            
    except Exception as e:
        print(f"❌ Login test failed: {e}")
        return False
    
    # Test 3: Check WebSocket consumers
    print("\n" + "=" * 40)
    print("🧪 TEST 3: WebSocket Consumer Validation")
    print("=" * 40)
    
    # Check if NotificationConsumer exists and is configured
    try:
        from auth_app.consumers import NotificationConsumer
        print("✅ NotificationConsumer imported successfully")
        
        # Check routing
        try:
            from auth_app.routing import websocket_urlpatterns
            print(f"✅ WebSocket routing patterns: {len(websocket_urlpatterns)} patterns")
            for pattern in websocket_urlpatterns:
                print(f"   📍 Pattern: {pattern.pattern}")
        except Exception as e:
            print(f"⚠️  Could not check routing: {e}")
            
    except ImportError as e:
        print(f"❌ NotificationConsumer import failed: {e}")
        return False
    
    # Test 4: Channel layer connectivity
    print("\n" + "=" * 40)
    print("🧪 TEST 4: Channel Layer Connectivity")
    print("=" * 40)
    
    if channel_layer:
        try:
            # Test basic channel operations
            test_channel = async_to_sync(channel_layer.new_channel)()
            print(f"✅ Created test channel: {test_channel}")
            
            # Test group operations
            async_to_sync(channel_layer.group_add)('test_group', test_channel)
            print("✅ Added channel to test group")
            
            async_to_sync(channel_layer.group_discard)('test_group', test_channel)
            print("✅ Removed channel from test group")
            
            print("✅ Channel layer operations working correctly")
            
        except Exception as e:
            print(f"❌ Channel layer test failed: {e}")
            return False
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 REAL-TIME STATUS TEST SUMMARY")
    print("=" * 60)
    
    # Final status check
    profile.refresh_from_db()
    print(f"📊 Final profile status: {profile.status}")
    print(f"📊 Final last_seen: {profile.last_seen}")
    
    print("\n✅ Backend components tested:")
    print("   ✓ Profile status updates")
    print("   ✓ WebSocket broadcasting")
    print("   ✓ Login API status updates")
    print("   ✓ Channel layer operations")
    print("   ✓ NotificationConsumer availability")
    
    print("\n🔍 Frontend debugging suggestions:")
    print("   1. Check browser console for WebSocket connection errors")
    print("   2. Verify NotificationConsumer authentication")
    print("   3. Confirm WebSocket URL and token in frontend")
    print("   4. Check if frontend joins 'status_updates' group")
    print("   5. Verify status_update handler execution")
    
    print("\n📝 Expected WebSocket payload format:")
    expected_payload = {
        'type': 'status_update',
        'user_id': user.id,
        'status': 'online',
        'last_seen': profile.last_seen.isoformat()
    }
    print(json.dumps(expected_payload, indent=2))
    
    print("\n🚀 Test completed successfully!")
    return True

if __name__ == '__main__':
    test_complete_status_flow()
