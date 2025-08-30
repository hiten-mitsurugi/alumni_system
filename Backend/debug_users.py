#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser

print("=== ALL USERS IN DATABASE ===")
users = CustomUser.objects.all()
for user in users:
    full_name_no_space = (user.first_name + user.last_name).lower().replace(' ', '')
    print(f"ID: {user.id}")
    print(f"Username: {user.username}")
    print(f"First Name: '{user.first_name}'")
    print(f"Last Name: '{user.last_name}'")
    print(f"Full Name: '{user.first_name} {user.last_name}'")
    print(f"Name No Space: '{full_name_no_space}'")
    print(f"Is Approved: {user.is_approved}")
    print(f"Is Active: {user.is_active}")
    print("-" * 50)

print(f"\nTotal users: {users.count()}")

# Test specific searches
test_names = ['romanosorio', 'mariaelenagarcia', 'maria', 'roman']
print(f"\n=== TESTING NAME SEARCHES ===")
for test_name in test_names:
    print(f"\nSearching for: '{test_name}'")
    
    # Try different search methods
    users = CustomUser.objects.filter(
        username__icontains=test_name.lower()
    ).filter(is_approved=True, is_active=True)
    print(f"Username contains '{test_name}': {users.count()} results")
    
    users = CustomUser.objects.filter(
        first_name__icontains=test_name.lower()
    ).filter(is_approved=True, is_active=True)
    print(f"First name contains '{test_name}': {users.count()} results")
    
    users = CustomUser.objects.filter(
        last_name__icontains=test_name.lower()
    ).filter(is_approved=True, is_active=True)
    print(f"Last name contains '{test_name}': {users.count()} results")
    
    # Test full name concatenation
    all_users = CustomUser.objects.filter(is_approved=True, is_active=True)
    matches = []
    for user in all_users:
        full_name_no_space = (user.first_name + user.last_name).lower().replace(' ', '')
        if full_name_no_space == test_name.lower():
            matches.append(user)
    print(f"Full name matches '{test_name}': {len(matches)} results")
    for match in matches:
        print(f"  - {match.first_name} {match.last_name} (ID: {match.id})")
