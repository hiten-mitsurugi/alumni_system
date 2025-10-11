#!/usr/bin/env python
import os
import sys
import django
import json

# Add the project directory to the Python path
sys.path.insert(0, os.path.dirname(__file__))

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.serializers import RegisterSerializer
from auth_app.models import CustomUser, Address

def test_address_serialization():
    """Test if address data is properly saved with the JSON field fix"""
    
    print("=== Testing Address Data Serialization Fix ===")
    
    # Sample address data exactly as it would come from frontend
    test_data = {
        'first_name': 'Test',
        'middle_name': 'Address',
        'last_name': 'User',
        'email': 'testaddress@example.com',
        'password': 'TestPassword123!',
        'confirm_password': 'TestPassword123!',
        'contact_number': '09123456789',
        'sex': 'male',
        'birth_date': '1990-01-01',
        'year_graduated': 2015,
        'program': 'Computer Science',
        'employment_status': 'employed',
        'civil_status': 'single',
        'mothers_name': 'Test Mother',
        'mothers_occupation': 'Teacher',
        'fathers_name': 'Test Father',
        'fathers_occupation': 'Engineer',
        'alumni_exists': False,
        
        # Address data as JSON strings (like FormData sends)
        'present_address_data': json.dumps({
            'address_type': 'philippines',
            'region_code': '01',
            'region_name': 'Ilocos Region',
            'province_code': '0128',
            'province_name': 'Ilocos Norte',
            'city_code': '012801',
            'city_name': 'Laoag City',
            'barangay': 'Barangay 1',
            'street_address': '123 Test Street',
            'postal_code': '2900',
            'country': 'Philippines',
            'full_address': '123 Test Street, Barangay 1, Laoag City, Ilocos Norte, Philippines 2900'
        }),
        'permanent_address_data': json.dumps({
            'address_type': 'philippines',
            'region_code': '05',
            'region_name': 'Bicol Region',
            'province_code': '0520',
            'province_name': 'Albay',
            'city_code': '052002',
            'city_name': 'Legazpi City',
            'barangay': 'Barangay Centro',
            'street_address': '456 Another Street',
            'postal_code': '4500',
            'country': 'Philippines',
            'full_address': '456 Another Street, Barangay Centro, Legazpi City, Albay, Philippines 4500'
        })
    }
    
    try:
        # Test serializer validation
        serializer = RegisterSerializer(data=test_data)
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            
            # Test user creation
            user = serializer.save()
            print(f"✅ User created: {user.email}")
            
            # Check if addresses were created
            addresses = Address.objects.filter(user=user)
            print(f"✅ Number of addresses created: {addresses.count()}")
            
            for address in addresses:
                print(f"\n--- {address.address_category.title()} Address ---")
                print(f"Address Type: {address.address_type}")
                print(f"Region: {address.region_name} ({address.region_code})")
                print(f"Province: {address.province_name} ({address.province_code})")
                print(f"City: {address.city_name} ({address.city_code})")
                print(f"Barangay: {address.barangay}")
                print(f"Street: {address.street_address}")
                print(f"Postal Code: {address.postal_code}")
                print(f"Country: {address.country}")
                print(f"Full Address: {address.full_address}")
                
                # Check if the critical fields are populated
                if address.region_name and address.city_name:
                    print("✅ Address data saved correctly!")
                else:
                    print("❌ Address data is missing!")
        else:
            print("❌ Serializer validation failed:")
            for field, errors in serializer.errors.items():
                print(f"  {field}: {errors}")
                
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up test data
        try:
            test_user = CustomUser.objects.get(email='testaddress@example.com')
            test_user.delete()
            print("\n🧹 Test data cleaned up")
        except CustomUser.DoesNotExist:
            pass

if __name__ == '__main__':
    test_address_serialization()