#!/usr/bin/env python
"""
Check what's actually in the achievement database
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, '/c/Users/USER/OneDrive/Desktop/Thesis/development/alumni_system/Backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import Achievement
from django.contrib.auth import get_user_model

User = get_user_model()

def check_achievements_in_db():
    print("🔍 Checking Achievement records in database...")
    
    achievements = Achievement.objects.all().order_by('-created_at')[:5]
    
    print(f"📊 Found {achievements.count()} achievements in database")
    
    for i, ach in enumerate(achievements, 1):
        print(f"\n📋 Achievement #{i} (ID: {ach.id}):")
        print(f"  Title: '{ach.title}'")
        print(f"  Type: '{ach.type}' (length: {len(ach.type) if ach.type else 0})")
        print(f"  Organization: '{ach.organization}'")
        print(f"  Date: {ach.date_achieved}")
        print(f"  URL: '{ach.url}' (length: {len(ach.url) if ach.url else 0})")
        print(f"  Description: '{ach.description[:50]}...' (length: {len(ach.description) if ach.description else 0})")
        print(f"  Attachment: '{ach.attachment}' (exists: {bool(ach.attachment)})")
        print(f"  Is Featured: {ach.is_featured}")
        print(f"  User: {ach.user}")
        print(f"  Created: {ach.created_at}")
        
        # Check if fields are empty strings vs None
        print(f"  🔍 Field Analysis:")
        print(f"    Type is None: {ach.type is None}, is empty: {ach.type == ''}")
        print(f"    URL is None: {ach.url is None}, is empty: {ach.url == ''}")
        print(f"    Attachment is None: {not ach.attachment}, exists: {bool(ach.attachment)}")

if __name__ == "__main__":
    check_achievements_in_db()