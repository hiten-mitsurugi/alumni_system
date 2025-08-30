#!/usr/bin/env python
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser

print("=== ALL ACTIVE USERS ===")
users = CustomUser.objects.filter(is_active=True, is_approved=True)
for user in users:
    name_identifier = (user.first_name + user.last_name).lower().replace(' ', '')
    print(f"ID: {user.id}, Name: {user.first_name} {user.last_name}, Username: {user.username}, Identifier: {name_identifier}")

print(f"\nTotal users: {users.count()}")

# Test specific name
test_name = "romanosorio"
print(f"\n=== TESTING NAME: {test_name} ===")

# Test the NEW query logic from the view
print(f"\n=== TESTING NEW LOGIC FOR: {test_name} ===")

users = CustomUser.objects.filter(is_approved=True, is_active=True)
found_user = None

for user in users:
    full_name_no_space = (user.first_name + user.last_name).lower().replace(' ', '')
    exact_match = full_name_no_space == test_name.lower()
    print(f"  - {user.first_name} {user.last_name} (ID: {user.id}) - Identifier: '{full_name_no_space}' - Exact match: {exact_match}")
    if exact_match:
        found_user = user

if found_user:
    print(f"\n✅ SUCCESS: Found user {found_user.first_name} {found_user.last_name} (ID: {found_user.id})")
else:
    print(f"\n❌ FAILED: No user found for '{test_name}'")
