#!/usr/bin/env python
import os
import django
import sys
import json
from io import BytesIO
from PIL import Image

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from auth_app.models import Achievement
from auth_app.serializers import AchievementSerializer

def test_model_directly():
    """Test 1: Direct model creation to verify the model itself works"""
    print("🧪 TEST 1: Direct Model Creation")
    print("=" * 50)
    
    try:
        User = get_user_model()
        user = User.objects.filter(username='superadmin').first()
        
        if not user:
            print("❌ No superadmin user found")
            return False
            
        # Create achievement directly using model
        achievement = Achievement.objects.create(
            user=user,
            title='Direct Model Test',
            type='award',
            description='Testing direct model creation',
            organization='Test Org',
            date_achieved='2024-05-15',
            url='https://direct-model.test',
            is_featured=True
        )
        
        print(f"✅ Direct model creation successful:")
        print(f"   ID: {achievement.id}")
        print(f"   Title: {achievement.title}")
        print(f"   Type: '{achievement.type}'")
        print(f"   URL: {achievement.url}")
        print(f"   Organization: {achievement.organization}")
        print(f"   Is Featured: {achievement.is_featured}")
        
        # Clean up
        achievement.delete()
        print("🗑️  Cleaned up direct model test")
        return True
        
    except Exception as e:
        print(f"❌ Direct model test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_serializer_directly():
    """Test 2: Direct serializer usage"""
    print("\n🧪 TEST 2: Direct Serializer Usage")
    print("=" * 50)
    
    try:
        User = get_user_model()
        user = User.objects.filter(username='superadmin').first()
        
        if not user:
            print("❌ No superadmin user found")
            return False
            
        # Test data for serializer
        test_data = {
            'title': 'Serializer Test Achievement',
            'type': 'certification',
            'description': 'Testing serializer creation',
            'organization': 'Serializer Test Org',
            'date_achieved': '2024-06-15',
            'url': 'https://serializer-test.example.com',
            'is_featured': False
        }
        
        print(f"📤 Input data: {test_data}")
        
        # Create using serializer
        serializer = AchievementSerializer(data=test_data)
        
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            print(f"📋 Validated data: {serializer.validated_data}")
            
            # Save with user
            achievement = serializer.save(user=user)
            
            print(f"✅ Serializer creation successful:")
            print(f"   ID: {achievement.id}")
            print(f"   Title: {achievement.title}")
            print(f"   Type: '{achievement.type}'")
            print(f"   URL: {achievement.url}")
            print(f"   Organization: {achievement.organization}")
            print(f"   Is Featured: {achievement.is_featured}")
            
            # Verify in database
            saved = Achievement.objects.get(id=achievement.id)
            print(f"🔍 Database verification:")
            print(f"   Type from DB: '{saved.type}'")
            print(f"   URL from DB: {saved.url}")
            
            # Clean up
            achievement.delete()
            print("🗑️  Cleaned up serializer test")
            return True
        else:
            print(f"❌ Serializer validation failed: {serializer.errors}")
            return False
            
    except Exception as e:
        print(f"❌ Serializer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_with_form_data():
    """Test 3: API with form data (multipart)"""
    print("\n🧪 TEST 3: API with Form Data")
    print("=" * 50)
    
    try:
        client = Client()
        User = get_user_model()
        user = User.objects.filter(username='superadmin').first()
        
        if not user:
            print("❌ No superadmin user found")
            return False
            
        # Login the user
        client.force_login(user)
        
        # Create a simple test file
        image = Image.new('RGB', (50, 50), color='blue')
        image_io = BytesIO()
        image.save(image_io, format='JPEG')
        image_io.seek(0)
        
        test_file = SimpleUploadedFile(
            "api_test.jpg",
            image_io.read(),
            content_type="image/jpeg"
        )
        
        # Test data for API
        test_data = {
            'title': 'API Form Test',
            'type': 'professional',
            'description': 'Testing API with form data',
            'organization': 'API Test Org',
            'date_achieved': '2024-07-15',
            'url': 'https://api-test.example.com/certificate',
            'is_featured': True,
            'attachment': test_file
        }
        
        print(f"📤 Sending to API: {dict((k, v if k != 'attachment' else 'api_test.jpg') for k, v in test_data.items())}")
        
        # Send POST request
        response = client.post('/api/auth/achievements/', data=test_data, format='multipart')
        
        print(f"📥 Response status: {response.status_code}")
        
        if response.status_code == 201:
            response_data = json.loads(response.content.decode())
            achievement_id = response_data.get('id')
            
            print(f"✅ API creation successful:")
            print(f"   Response data: {response_data}")
            
            # Verify in database
            saved_achievement = Achievement.objects.get(id=achievement_id)
            print(f"🔍 Database verification:")
            print(f"   Title: '{saved_achievement.title}'")
            print(f"   Type: '{saved_achievement.type}'")
            print(f"   URL: {saved_achievement.url}")
            print(f"   Organization: '{saved_achievement.organization}'")
            print(f"   Attachment: {saved_achievement.attachment}")
            print(f"   Is Featured: {saved_achievement.is_featured}")
            
            # Check for missing fields
            missing_fields = []
            if not saved_achievement.type: missing_fields.append('type')
            if not saved_achievement.url: missing_fields.append('url')
            if not saved_achievement.attachment: missing_fields.append('attachment')
            
            if missing_fields:
                print(f"❌ Missing fields in database: {missing_fields}")
                return False
            else:
                print("✅ All fields saved correctly!")
                
            # Clean up
            saved_achievement.delete()
            print("🗑️  Cleaned up API test")
            return True
        else:
            print(f"❌ API request failed")
            print(f"❌ Response: {response.content.decode()}")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_raw_request_data():
    """Test 4: Check what raw request data looks like"""
    print("\n🧪 TEST 4: Raw Request Data Analysis")
    print("=" * 50)
    
    try:
        from django.test import RequestFactory
        from auth_app.views import AchievementListCreateView
        from django.contrib.auth.models import AnonymousUser
        
        User = get_user_model()
        user = User.objects.filter(username='superadmin').first()
        
        if not user:
            print("❌ No superadmin user found")
            return False
        
        factory = RequestFactory()
        
        # Create test data
        test_data = {
            'title': 'Raw Request Test',
            'type': 'award',
            'description': 'Testing raw request',
            'organization': 'Raw Test Org',
            'date_achieved': '2024-08-15',
            'url': 'https://raw-test.example.com',
            'is_featured': 'false'
        }
        
        print(f"📤 Raw test data: {test_data}")
        
        # Create request
        request = factory.post('/api/auth/achievements/', data=test_data)
        request.user = user
        
        print(f"📋 Request.POST: {dict(request.POST)}")
        print(f"📋 Request.data (if exists): {getattr(request, 'data', 'No data attribute')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Raw request test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all backend tests"""
    print("🚀 BACKEND COMPREHENSIVE ACHIEVEMENT TESTS")
    print("=" * 80)
    
    results = {
        'model_direct': test_model_directly(),
        'serializer_direct': test_serializer_directly(), 
        'api_form_data': test_api_with_form_data(),
        'raw_request': test_raw_request_data()
    }
    
    print("\n📊 TEST RESULTS SUMMARY")
    print("=" * 50)
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    print(f"\nOverall: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("🎉 All backend tests passed!")
    else:
        print("⚠️  Some backend tests failed - issue identified!")

if __name__ == "__main__":
    run_all_tests()