#!/usr/bin/env python
"""
Test script to manually broadcast a status update and verify the WebSocket system is working.
Run this from the Django shell to test the status broadcast system.
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

def test_status_broadcast():
    """Test broadcasting a status update to all connected clients"""
    
    # Get the first user for testing
    user = CustomUser.objects.filter(user_type=3).first()
    if not user:
        print("No alumni users found for testing")
        return
    
    print(f"Testing status broadcast for user {user.id} ({user.first_name} {user.last_name})")
    
    # Create or get profile
    profile, created = Profile.objects.get_or_create(user=user)
    profile.status = 'offline'  # Set to offline for testing
    profile.last_seen = timezone.now()
    profile.save()
    
    print(f"Set user {user.id} status to offline in database")
    
    # Try to broadcast the status update
    try:
        channel_layer = get_channel_layer()
        status_payload = {
            'type': 'status_update',
            'user_id': user.id,
            'status': 'offline',
            'last_seen': profile.last_seen.isoformat()
        }
        
        print(f"Broadcasting status update: {status_payload}")
        
        async_to_sync(channel_layer.group_send)(
            'status_updates',  # Global status updates group
            status_payload
        )
        
        print("Status update broadcast successful!")
        print("Check the frontend console to see if the message was received")
        
    except Exception as e:
        print(f"Status broadcast failed: {str(e)}")
        
if __name__ == "__main__":
    test_status_broadcast()
