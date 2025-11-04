#!/usr/bin/env python
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import Profile
import inspect

source = inspect.getsource(Profile.save)
print("Current Profile.save() method:")
print("="*80)
print(source)
print("="*80)

if 'is_current_job' in source:
    print("\n❌ PROBLEM: is_current_job query STILL in code!")
    print("Need to investigate further...")
else:
    print("\n✅ GOOD: is_current_job query removed")
