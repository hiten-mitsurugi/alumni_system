#!/usr/bin/env python
import os
import sys
import django

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser, Following

def check_mention_system():
    print("=== DEBUGGING @MENTION SYSTEM ===\n")
    
    # Check if users 4 and 5 exist
    print("1. Checking if users exist:")
    try:
        user4 = CustomUser.objects.get(id=4)
        print(f"   ✓ User 4: {user4.username} ({user4.first_name} {user4.last_name}) - Type: {user4.user_type}")
    except CustomUser.DoesNotExist:
        print("   ✗ User 4 does not exist!")
        return
    
    try:
        user5 = CustomUser.objects.get(id=5)
        print(f"   ✓ User 5: {user5.username} ({user5.first_name} {user5.last_name}) - Type: {user5.user_type}")
    except CustomUser.DoesNotExist:
        print("   ✗ User 5 does not exist!")
        return
    
    print()
    
    # Check user approval status
    print("2. Checking user approval status:")
    print(f"   User 4 - is_active: {user4.is_active}, is_approved: {user4.is_approved}")
    print(f"   User 5 - is_active: {user5.is_active}, is_approved: {user5.is_approved}")
    print()
    
    # Check following relationships
    print("3. Checking following relationships:")
    
    # User 4 following User 5
    follow_4_to_5 = Following.objects.filter(follower=user4, following=user5).first()
    if follow_4_to_5:
        print(f"   ✓ User 4 follows User 5 - Status: {follow_4_to_5.status}")
    else:
        print("   ✗ User 4 does NOT follow User 5")
    
    # User 5 following User 4  
    follow_5_to_4 = Following.objects.filter(follower=user5, following=user4).first()
    if follow_5_to_4:
        print(f"   ✓ User 5 follows User 4 - Status: {follow_5_to_4.status}")
    else:
        print("   ✗ User 5 does NOT follow User 4")
    
    print()
    
    # Test mention search for user 4
    print("4. Testing mention search for User 4:")
    
    # Get user 4's connections
    following_ids = Following.objects.filter(
        follower=user4,
        status='accepted'
    ).values_list('following_id', flat=True)
    
    print(f"   User 4's connections (IDs): {list(following_ids)}")
    
    # Search for user 5 by various queries
    queries = [user5.first_name, user5.last_name, user5.username, user5.first_name[:3]]
    
    for query in queries:
        print(f"\n   Testing query: '{query}'")
        
        # Search in connections first
        connection_users = CustomUser.objects.filter(
            id__in=following_ids,
            is_active=True,
            is_approved=True
        ).filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(username__icontains=query) |
            Q(email__icontains=query)
        ).exclude(id=user4.id)
        
        print(f"     - Found in connections: {list(connection_users.values_list('username', 'first_name', 'last_name'))}")
        
        # Search in all users if not found in connections
        if not connection_users.exists():
            all_users = CustomUser.objects.filter(
                is_active=True,
                is_approved=True,
                user_type=3  # Alumni
            ).filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(username__icontains=query) |
                Q(email__icontains=query)
            ).exclude(id=user4.id)
            
            print(f"     - Found in all users: {list(all_users.values_list('username', 'first_name', 'last_name'))}")

if __name__ == "__main__":
    from django.db.models import Q
    check_mention_system()