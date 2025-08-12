#!/usr/bin/env python
import os
import sys
import django

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import CustomUser
from auth_app.serializers import UserDetailSerializer

def test_admin_profile():
    print("=== Testing Admin Profile Update ===")
    
    # Find admin user
    try:
        admin_user = CustomUser.objects.get(email="admin@alumni.com")
        print(f"Found admin user: {admin_user.first_name} {admin_user.last_name}")
        print(f"User type: {admin_user.user_type}")
        print(f"Is authenticated: {admin_user.is_authenticated}")
        print(f"User ID: {admin_user.id}")
        
        # Test serializer
        test_data = {
            'first_name': 'Updated Admin',
            'contact_number': '123-456-7890'
        }
        
        serializer = UserDetailSerializer(admin_user, data=test_data, partial=True)
        print(f"Serializer is valid: {serializer.is_valid()}")
        
        if not serializer.is_valid():
            print(f"Serializer errors: {serializer.errors}")
        else:
            print("Serializer validation passed!")
            print(f"Validated data: {serializer.validated_data}")
            
            # Test actual update without saving
            for field, value in serializer.validated_data.items():
                print(f"Would update {field}: {getattr(admin_user, field)} -> {value}")
                
    except CustomUser.DoesNotExist:
        print("Admin user not found!")
        print("Available users:")
        for user in CustomUser.objects.all():
            print(f"  - {user.email} (Type: {user.user_type})")

if __name__ == "__main__":
    test_admin_profile()
