#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from auth_app.models import Following

User = get_user_model()

print('Users in system:')
for u in User.objects.all():
    print(f'  {u.id}: {u.email} ({u.first_name} {u.last_name})')

print('\nFollowing relationships:')
for f in Following.objects.all():
    print(f'  {f.follower.email} -> {f.following.email} (status: {f.status})')