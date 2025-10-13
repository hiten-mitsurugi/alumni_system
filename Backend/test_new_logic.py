#!/usr/bin/env python
import os
import django
import sys

# Add the Backend directory to the path
sys.path.append('.')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser, Following
from auth_app.views.profile_social import SuggestedConnectionsView
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from rest_framework.test import APIRequestFactory

def test_new_logic():
    print("=" * 50)
    print("TESTING NEW SUGGESTIONS LOGIC")
    print("=" * 50)
    
    try:
        user = CustomUser.objects.get(id=7)
        print(f"Testing with user: {user.email}")
        print(f"Program: {user.program}")
        print(f"Year: {user.year_graduated}")
        
        # Test the new logic directly
        from django.db.models import Q
        from auth_app.models import Following
        
        connected_user_ids = Following.objects.filter(
            Q(follower=user) | Q(following=user)
        ).values_list('follower_id', 'following_id')
        
        exclude_ids = set()
        for follower_id, following_id in connected_user_ids:
            exclude_ids.add(follower_id)
            exclude_ids.add(following_id)
        exclude_ids.add(user.id)
        
        print(f"Excluded IDs: {exclude_ids}")
        
        # Get base suggestions (all approved alumni except connected ones)
        base_suggestions = CustomUser.objects.filter(
            user_type=3, 
            is_approved=True, 
            is_active=True
        ).exclude(id__in=exclude_ids)
        
        print(f"Base suggestions count: {base_suggestions.count()}")
        
        # New prioritization logic
        priority_suggestions = []
        regular_suggestions = []
        
        for suggestion in base_suggestions:
            print(f"  Checking user {suggestion.id}: {suggestion.email}")
            print(f"    Program: {suggestion.program}")
            print(f"    Year: {suggestion.year_graduated}")
            
            # Priority 1: Same program OR same year
            if ((user.program and suggestion.program == user.program) or 
                (user.year_graduated and suggestion.year_graduated == user.year_graduated)):
                print(f"    -> PRIORITY (same program or year)")
                priority_suggestions.append(suggestion)
            else:
                print(f"    -> REGULAR")
                regular_suggestions.append(suggestion)
        
        # Combine prioritized suggestions first, then regular ones
        final_suggestions = priority_suggestions + regular_suggestions
        
        print(f"\nPriority suggestions: {len(priority_suggestions)}")
        print(f"Regular suggestions: {len(regular_suggestions)}")
        print(f"Total final suggestions: {len(final_suggestions)}")
        
        if len(final_suggestions) > 0:
            print("✅ SUCCESS! Suggestions are now being returned.")
            for i, suggestion in enumerate(final_suggestions):
                print(f"  {i+1}. {suggestion.email} (ID: {suggestion.id})")
        else:
            print("❌ Still no suggestions returned.")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_new_logic()