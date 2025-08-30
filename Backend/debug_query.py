#!/usr/bin/env python
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser
from django.db.models import Q

test_name = 'romanosorio'
print(f"=== DEBUGGING QUERY FOR '{test_name}' ===")

# Check all users first
all_users = CustomUser.objects.filter(is_approved=True, is_active=True)
print(f"Total approved/active users: {all_users.count()}")

for user in all_users:
    full_name_no_space = (user.first_name + user.last_name).lower().replace(' ', '')
    print(f"User: {user.first_name} {user.last_name}")
    print(f"  - Username: {user.username}")
    print(f"  - Full name no space: '{full_name_no_space}'")
    print(f"  - Target: '{test_name.lower()}'")
    print(f"  - Match: {full_name_no_space == test_name.lower()}")
    print()

# Test individual query parts
print("=== TESTING INDIVIDUAL QUERY PARTS ===")

# Test username exact match
q1 = CustomUser.objects.filter(username__iexact=test_name)
print(f"username__iexact='{test_name}': {q1.count()} results")

# Test first name contains
q2 = CustomUser.objects.filter(first_name__icontains=test_name.lower())
print(f"first_name__icontains='{test_name.lower()}': {q2.count()} results")

# Test last name contains  
q3 = CustomUser.objects.filter(last_name__icontains=test_name.lower())
print(f"last_name__icontains='{test_name.lower()}': {q3.count()} results")

# Test the combined query
combined_q = CustomUser.objects.filter(
    Q(username__iexact=test_name) |
    Q(first_name__icontains=test_name.lower()) |
    Q(last_name__icontains=test_name.lower())
)
print(f"Combined query (before filter): {combined_q.count()} results")

# Apply the approved/active filter
final_q = combined_q.filter(is_approved=True, is_active=True)
print(f"Final query (after approved/active filter): {final_q.count()} results")

# Check if Roman Osorio exists and his status
roman_user = CustomUser.objects.filter(first_name__iexact='Roman', last_name__iexact='Osorio').first()
if roman_user:
    print(f"\n=== ROMAN OSORIO STATUS ===")
    print(f"Found Roman Osorio: ID {roman_user.id}")
    print(f"  - Username: {roman_user.username}")
    print(f"  - Is approved: {roman_user.is_approved}")
    print(f"  - Is active: {roman_user.is_active}")
    print(f"  - Full name concatenated: '{(roman_user.first_name + roman_user.last_name).lower()}'")
else:
    print("\n❌ Roman Osorio not found in database!")
