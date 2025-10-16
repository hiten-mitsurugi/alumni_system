#!/usr/bin/env python3
"""
Check available superadmin users and test the export endpoint configuration.
"""

import os
import sys
import django
from django.urls import reverse
from django.test import Client

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.urls import resolve, Resolver404

def check_system_state():
    """Check the current system state for debugging."""
    print("🔍 System State Check")
    print("=" * 50)
    
    User = get_user_model()
    
    # Check available users
    print("1. Available Super Admin Users:")
    superadmins = User.objects.filter(user_type=1)  # Assuming 1 is superadmin
    if superadmins.exists():
        for admin in superadmins:
            print(f"   - {admin.email} (ID: {admin.id}, Active: {admin.is_active})")
    else:
        print("   No superadmin users found with user_type=1")
        
        # Check other admin users
        admins = User.objects.filter(is_superuser=True)
        if admins.exists():
            print("   Django superusers found:")
            for admin in admins:
                print(f"   - {admin.email} (ID: {admin.id}, Active: {admin.is_active})")
        else:
            print("   No Django superusers found either")
    
    # Check URL resolution
    print("\n2. URL Resolution Test:")
    try:
        # Test the URL pattern
        resolved = resolve('/api/survey/admin/export/')
        print(f"   ✅ URL resolves to: {resolved.func.__name__}")
        print(f"   View module: {resolved.func.__module__}")
        print(f"   Namespace: {resolved.namespace}")
        print(f"   URL name: {resolved.url_name}")
    except Resolver404 as e:
        print(f"   ❌ URL resolution failed: {e}")
    except Exception as e:
        print(f"   ❌ URL resolution error: {e}")
    
    # Test with Django test client
    print("\n3. Django Test Client Test:")
    client = Client()
    
    # Find a superadmin to test with
    superadmin = User.objects.filter(user_type=1).first()
    if not superadmin:
        superadmin = User.objects.filter(is_superuser=True).first()
    
    if superadmin:
        print(f"   Testing with user: {superadmin.email}")
        client.force_login(superadmin)
        
        # Test POST request
        try:
            response = client.post('/api/survey/admin/export/', 
                                 data={'format': 'json'},
                                 content_type='application/json')
            print(f"   POST Status: {response.status_code}")
            if response.status_code == 405:
                print("   ❌ 405 Method Not Allowed confirmed")
                # Check what methods are allowed
                allowed_methods = response.get('Allow', 'Not specified')
                print(f"   Allowed methods: {allowed_methods}")
            else:
                print(f"   Response: {response.status_code}")
        except Exception as e:
            print(f"   POST error: {e}")
            
        # Test GET request
        try:
            response = client.get('/api/survey/admin/export/', {'format': 'json'})
            print(f"   GET Status: {response.status_code}")
        except Exception as e:
            print(f"   GET error: {e}")
    else:
        print("   No admin user available for testing")
    
    # Check view function directly
    print("\n4. View Function Check:")
    try:
        from survey_app.views import survey_export_view
        print(f"   ✅ View function exists: {survey_export_view}")
        print(f"   Function: {survey_export_view.__name__}")
        
        # Check decorators
        if hasattr(survey_export_view, '__wrapped__'):
            print("   Function has decorators")
        
    except ImportError as e:
        print(f"   ❌ Cannot import view: {e}")
    except Exception as e:
        print(f"   ❌ View check error: {e}")

if __name__ == '__main__':
    check_system_state()