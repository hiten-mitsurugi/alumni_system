import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.conf import settings
from django_cryptography.core.signing import Signer
from messaging_app.models import Message

print("=" * 60)
print("ENCRYPTION CONFIGURATION CHECK")
print("=" * 60)

print(f"\n1. SECRET_KEY length: {len(settings.SECRET_KEY)} chars")
print(f"   First 50 chars: {settings.SECRET_KEY[:50]}")
print(f"   Last 20 chars: {settings.SECRET_KEY[-20:]}")

print(f"\n2. CRYPTOGRAPHY_SALT: {settings.CRYPTOGRAPHY_SALT}")
print(f"   Type: {type(settings.CRYPTOGRAPHY_SALT)}")

print(f"\n3. CRYPTOGRAPHY_BACKEND: {settings.CRYPTOGRAPHY_BACKEND}")

# Check a sample encrypted message
print("\n" + "=" * 60)
print("CHECKING SAMPLE ENCRYPTED MESSAGE")
print("=" * 60)

messages = Message.objects.all()[:3]
for msg in messages:
    print(f"\nMessage ID: {msg.id}")
    print(f"Sender: {msg.sender.username}")
    print(f"Timestamp: {msg.timestamp}")
    try:
        content = msg.content
        print(f"✅ Content decrypted: {content[:50]}...")
    except Exception as e:
        print(f"❌ Decryption failed: {type(e).__name__}: {str(e)[:100]}")
        
        # Try to see the raw encrypted value
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT content FROM messaging_app_message WHERE id = '{msg.id}'")
            raw_content = cursor.fetchone()[0]
            print(f"   Raw encrypted length: {len(raw_content)} bytes")
            print(f"   First 50 chars: {raw_content[:50]}")

print("\n" + "=" * 60)
print("DJANGO-CRYPTOGRAPHY SIGNER TEST")
print("=" * 60)

try:
    # Test if we can create a signer with current settings
    test_text = "Test message"
    from django_cryptography.fields import encrypt_str
    
    # Try encrypting with current config
    encrypted = encrypt_str(test_text)
    print(f"\n✅ Test encryption successful")
    print(f"   Encrypted length: {len(encrypted)} bytes")
    
    # Try decrypting
    from django_cryptography.fields import decrypt_str
    decrypted = decrypt_str(encrypted)
    print(f"✅ Test decryption successful: {decrypted}")
    
except Exception as e:
    print(f"\n❌ Encryption/decryption test failed: {e}")
