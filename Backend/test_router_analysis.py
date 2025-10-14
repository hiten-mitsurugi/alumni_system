#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from rest_framework.routers import DefaultRouter
from auth_app.views import UserViewSet

def test_router_urls():
    """Check what URLs the router is generating"""
    print("🔍 ROUTER URL ANALYSIS")
    print("=" * 50)
    
    try:
        router = DefaultRouter()
        router.register(r'users', UserViewSet)
        
        print("📋 Router URL patterns:")
        for pattern in router.urls:
            print(f"   {pattern.pattern}")
            
        print(f"\n📋 Total patterns: {len(router.urls)}")
        
        # Also check if UserViewSet has any nested routes
        print(f"\n🔍 UserViewSet inspection:")
        print(f"   Queryset: {UserViewSet.queryset}")
        print(f"   Serializer: {UserViewSet.serializer_class}")
        
        # Check for any actions or custom methods
        import inspect
        methods = inspect.getmembers(UserViewSet, predicate=inspect.ismethod)
        print(f"   Methods: {[name for name, _ in methods if not name.startswith('_')]}")
        
    except Exception as e:
        print(f"❌ Router analysis failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_router_urls()