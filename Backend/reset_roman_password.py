#!/usr/bin/env python
"""
Reset Roman Osorio's password to allow login
"""
import os
import django
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.contrib.auth import get_user_model

def reset_roman_password():
    """Reset Roman Osorio's password"""
    User = get_user_model()
    
    try:
        # Find Roman's account
        roman = User.objects.get(email='roman.osorio@carsu.edu.ph')
        
        print(f"Found account: {roman.email}")
        print(f"Username: {roman.username}")
        print(f"Active: {roman.is_active}")
        print(f"Last Login: {roman.last_login}")
        
        # Reset password to the preferred one
        new_password = "iloveyouLord143!"
        roman.set_password(new_password)
        roman.save()
        
        print(f"\n✅ Password reset successfully!")
        print(f"Email: {roman.email}")
        print(f"New Password: {new_password}")
        print(f"\nYou can now login with:")
        print(f"Email: roman.osorio@carsu.edu.ph")
        print(f"Password: {new_password}")
        
        # Verify the password works
        from django.contrib.auth import authenticate
        test_user = authenticate(username=roman.email, password=new_password)
        if test_user:
            print(f"\n✅ Password verification: SUCCESS")
        else:
            print(f"\n❌ Password verification: FAILED")
            
    except User.DoesNotExist:
        print("❌ Roman Osorio account not found!")
        print("Available Roman accounts:")
        roman_accounts = User.objects.filter(email__icontains='roman')
        for account in roman_accounts:
            print(f"  - {account.email}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    reset_roman_password()