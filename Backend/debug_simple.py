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

def debug_suggestions():
    print("=" * 50)
    print("DEBUG SUGGESTIONS ISSUE")
    print("=" * 50)
    
    # Check all users
    all_users = CustomUser.objects.all()
    print(f"Total users: {all_users.count()}")
    
    alumni_users = CustomUser.objects.filter(user_type=3)
    print(f"Alumni users (user_type=3): {alumni_users.count()}")
    
    approved_alumni = CustomUser.objects.filter(user_type=3, is_approved=True)
    print(f"Approved alumni: {approved_alumni.count()}")
    
    active_approved_alumni = CustomUser.objects.filter(user_type=3, is_approved=True, is_active=True)
    print(f"Active approved alumni: {active_approved_alumni.count()}")
    
    print("\n" + "=" * 30)
    print("USER DETAILS:")
    print("=" * 30)
    for user in all_users:
        print(f"ID: {user.id}, Email: {user.email}")
        print(f"  Type: {user.user_type}, Approved: {user.is_approved}, Active: {user.is_active}")
        print(f"  Program: {user.program}, Year: {user.year_graduated}")
        print(f"  Username: {user.username}")
        print()
    
    # Test the filtering logic from profile_social.py
    print("=" * 30)
    print("TESTING USER ID 7 (from logs):")
    print("=" * 30)
    
    try:
        user = CustomUser.objects.get(id=7)
        print(f"Current user: {user.email}")
        print(f"Program: {user.program}")
        print(f"Year graduated: {user.year_graduated}")
        
        # Test the filtering from profile_social.py
        from auth_app.models import Following
        from django.db.models import Q
        
        connected_user_ids = Following.objects.filter(
            Q(follower=user) | Q(following=user)
        ).values_list('follower_id', 'following_id')
        
        exclude_ids = set()
        for follower_id, following_id in connected_user_ids:
            exclude_ids.add(follower_id)
            exclude_ids.add(following_id)
        exclude_ids.add(user.id)
        
        print(f"Excluded IDs: {exclude_ids}")
        
        # Base suggestions
        base_suggestions = CustomUser.objects.filter(
            user_type=3, 
            is_approved=True, 
            is_active=True
        ).exclude(id__in=exclude_ids)
        
        print(f"Base suggestions count: {base_suggestions.count()}")
        
        # Apply program filter
        if user.program:
            filtered_by_program = base_suggestions.filter(program=user.program)
            print(f"After program filter: {filtered_by_program.count()}")
        else:
            print("No program set - this might be the issue!")
            
        # Apply year filter  
        if user.year_graduated:
            filtered_by_year = base_suggestions.filter(year_graduated=user.year_graduated)
            print(f"After year filter: {filtered_by_year.count()}")
        else:
            print("No year_graduated set - this might be the issue!")
            
        # Final suggestions (this is the problem)
        final_suggestions = base_suggestions
        if user.program:
            final_suggestions = final_suggestions.filter(program=user.program)
        if user.year_graduated:
            final_suggestions = final_suggestions.filter(year_graduated=user.year_graduated)
            
        print(f"Final suggestions count: {final_suggestions.count()}")
        
        if final_suggestions.count() == 0:
            print("\n🚨 PROBLEM FOUND!")
            print("The current user likely has no program or year_graduated set,")
            print("or no other users match the same program/year combination.")
            print("\nSUGGESTED FIX: Modify the filtering logic to be less restrictive.")
        
    except CustomUser.DoesNotExist:
        print("User ID 7 not found")

if __name__ == "__main__":
    debug_suggestions()