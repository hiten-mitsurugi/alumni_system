#!/usr/bin/env python
import os
import django
import sys

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.db import connection
from auth_app.models import Achievement

def check_achievement_table():
    try:
        # Check if table exists by trying to query it
        count = Achievement.objects.count()
        print(f"✅ Achievement table exists with {count} records")
        
        # Check table structure (PostgreSQL)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns 
                WHERE table_name = 'auth_app_achievement'
                ORDER BY ordinal_position;
            """)
            columns = cursor.fetchall()
            
        print("\n📋 Achievement table structure:")
        for col in columns:
            name, type_name, nullable, default = col
            print(f"  - {name}: {type_name} {'NULLABLE' if nullable == 'YES' else 'NOT NULL'} {f'DEFAULT {default}' if default else ''}")
            
        # Check if attachment and url fields exist
        field_names = [col[0] for col in columns]
        if 'attachment' in field_names:
            print("✅ 'attachment' field exists")
        else:
            print("❌ 'attachment' field is missing!")
            
        if 'url' in field_names:
            print("✅ 'url' field exists")
        else:
            print("❌ 'url' field is missing!")
            
        # Try to get some sample data
        if count > 0:
            sample = Achievement.objects.first()
            print(f"\n📝 Sample Achievement data:")
            print(f"  Title: {sample.title}")
            print(f"  Type: {sample.type}")
            print(f"  URL: {sample.url}")
            print(f"  Attachment: {sample.attachment}")
            
    except Exception as e:
        print(f"❌ Error checking Achievement table: {e}")
        print("This likely means the Achievement table doesn't exist or has issues")

if __name__ == "__main__":
    check_achievement_table()