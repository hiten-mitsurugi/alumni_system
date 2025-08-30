#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.views import UserByNameView
print("✅ UserByNameView imported successfully!")

# Test the view logic manually
from auth_app.models import CustomUser
from django.db.models import Q

test_name = 'romanosorio'
print(f"\n=== TESTING VIEW LOGIC FOR '{test_name}' ===")

# Replicate the exact logic from UserByNameView
users = CustomUser.objects.filter(
    Q(username__iexact=test_name) |
    Q(first_name__icontains=test_name.lower()) |
    Q(last_name__icontains=test_name.lower())
).filter(is_approved=True, is_active=True)

print(f"Initial query result: {users.count()} users")
for user in users:
    print(f"  - {user.first_name} {user.last_name} (username: {user.username})")

# Try exact match
exact_match = None
for user in users:
    full_name_no_space = (user.first_name + user.last_name).lower().replace(' ', '')
    print(f"  Testing: '{full_name_no_space}' == '{test_name.lower()}'")
    if full_name_no_space == test_name.lower():
        exact_match = user
        break

if exact_match:
    print(f"✅ EXACT MATCH FOUND: {exact_match.first_name} {exact_match.last_name} (ID: {exact_match.id})")
else:
    print("❌ NO EXACT MATCH FOUND")
    if users.exists():
        partial_match = users.first()
        print(f"Would use partial match: {partial_match.first_name} {partial_match.last_name} (ID: {partial_match.id})")
    else:
        print("No users found at all!")

# Test URL pattern matching
print(f"\n=== TESTING URL PATTERN ===")
from django.urls import resolve, reverse
from django.test import RequestFactory

try:
    # Test if URL can be resolved
    resolved = resolve('/api/alumni/by-name/romanosorio/')
    print(f"✅ URL resolved to view: {resolved.func}")
    print(f"✅ URL kwargs: {resolved.kwargs}")
except Exception as e:
    print(f"❌ URL resolution failed: {e}")

try:
    # Test reverse URL generation
    url = reverse('user_by_name', kwargs={'user_name': 'romanosorio'})
    print(f"✅ Reverse URL: {url}")
except Exception as e:
    print(f"❌ Reverse URL failed: {e}")
