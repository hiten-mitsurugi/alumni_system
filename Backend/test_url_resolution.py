#!/usr/bin/env python
import os
import django
import sys
from django.urls import resolve
from django.test import Client

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

def test_url_resolution():
    """Test what view actually handles the achievements URL"""
    print("🔍 URL RESOLUTION TEST")
    print("=" * 50)
    
    try:
        # Test URL resolution
        test_paths = [
            '/api/auth/achievements/',
            '/api/achievements/',
            '/auth/achievements/',
            '/achievements/'
        ]
        
        for path in test_paths:
            try:
                match = resolve(path)
                print(f"✅ {path}")
                print(f"   View: {match.func}")
                print(f"   View class: {match.func.cls if hasattr(match.func, 'cls') else 'Not a class-based view'}")
                print(f"   URL name: {match.url_name}")
                print(f"   Namespace: {match.namespace}")
                print(f"   Args: {match.args}")
                print(f"   Kwargs: {match.kwargs}")
            except Exception as e:
                print(f"❌ {path}: {e}")
            print()
        
        # Also test with POST method context
        print("🔍 Testing with Django test client request context:")
        client = Client()
        
        # Don't actually make the request, just see what resolver would match
        from django.urls import reverse
        try:
            url = reverse('achievements_list_create')
            print(f"✅ achievements_list_create reverse URL: {url}")
        except Exception as e:
            print(f"❌ achievements_list_create reverse failed: {e}")
            
    except Exception as e:
        print(f"❌ URL resolution test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_url_resolution()