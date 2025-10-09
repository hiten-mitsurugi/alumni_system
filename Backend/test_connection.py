#!/usr/bin/env python
"""
Test PostgreSQL connection using the same credentials as Django
"""
import os
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
import django
django.setup()

from django.db import connection
from django.core.management.color import no_style
from django.db.utils import OperationalError

def test_connection():
    """Test database connection"""
    try:
        # Test basic connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()
            print(f"✅ PostgreSQL Connection Successful!")
            print(f"📊 Database Version: {version[0]}")
            
        # Test database existence
        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            db_name = cursor.fetchone()
            print(f"📁 Connected to database: {db_name[0]}")
            
        # List existing tables
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name;
            """)
            tables = cursor.fetchall()
            if tables:
                print(f"📋 Existing tables ({len(tables)}):")
                for table in tables:
                    print(f"   - {table[0]}")
            else:
                print("📋 No tables found (database is empty)")
                
        return True
        
    except OperationalError as e:
        print(f"❌ Database Connection Failed!")
        print(f"🔍 Error: {e}")
        
        # Provide specific help based on error type
        error_str = str(e).lower()
        if "does not exist" in error_str:
            print("\n💡 Solution: The database needs to be created.")
            print("   In pgAdmin, create a new database named 'alumni_system'")
        elif "authentication failed" in error_str:
            print("\n💡 Solution: Check your PostgreSQL credentials.")
            print("   Verify username/password in pgAdmin or .env file")
        elif "connection refused" in error_str:
            print("\n💡 Solution: PostgreSQL server is not running.")
            print("   Start PostgreSQL service in Windows Services")
        
        return False
        
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Testing PostgreSQL Connection...")
    print("=" * 50)
    
    # Show connection details (without password)
    from django.conf import settings
    db_config = settings.DATABASES['default']
    print(f"Host: {db_config['HOST']}")
    print(f"Port: {db_config['PORT']}")
    print(f"Database: {db_config['NAME']}")
    print(f"User: {db_config['USER']}")
    print("=" * 50)
    
    success = test_connection()
    
    if success:
        print("\n🎉 Ready to run migrations!")
    else:
        print("\n🛠️  Fix the connection issues above, then try again.")