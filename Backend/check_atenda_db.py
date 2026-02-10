import psycopg
import os
from decouple import config

# Get database connection params
db_host = config('DB_HOST')
db_port = config('DB_PORT')
db_user = config('DB_USER')
db_password = config('DB_PASSWORD')

# Connect to postgres database to check if atenda exists
try:
    conn = psycopg.connect(
        host=db_host,
        port=db_port,
        user=db_user,
        password=db_password,
        dbname='postgres'  # Connect to default postgres db to check if atenda exists
    )
    conn.autocommit = True
    cursor = conn.cursor()
    
    # Check if atenda database exists
    cursor.execute("SELECT 1 FROM pg_database WHERE datname = 'atenda'")
    exists = cursor.fetchone()
    
    if exists:
        print("✅ Database 'atenda' exists")
        
        # Connect to atenda to check migration status
        cursor.close()
        conn.close()
        
        conn_atenda = psycopg.connect(
            host=db_host,
            port=db_port,
            user=db_user,
            password=db_password,
            dbname='atenda'
        )
        cursor_atenda = conn_atenda.cursor()
        
        # Check if django_migrations table exists
        cursor_atenda.execute("""
            SELECT 1 FROM information_schema.tables 
            WHERE table_name = 'django_migrations'
        """)
        
        if cursor_atenda.fetchone():
            print("✅ django_migrations table exists")
            
            # Check auth_app migrations
            cursor_atenda.execute("""
                SELECT COUNT(*) FROM django_migrations 
                WHERE app = 'auth_app'
            """)
            count = cursor_atenda.fetchone()[0]
            print(f"📊 auth_app migrations applied: {count}")
            
            # Check latest migration
            cursor_atenda.execute("""
                SELECT name FROM django_migrations 
                WHERE app = 'auth_app' 
                ORDER BY id DESC LIMIT 1
            """)
            latest = cursor_atenda.fetchone()
            if latest:
                print(f"📌 Latest auth_app migration: {latest[0]}")
        else:
            print("⚠️  django_migrations table does NOT exist (fresh database)")
        
        cursor_atenda.close()
        conn_atenda.close()
    else:
        print("❌ Database 'atenda' does NOT exist")
        print("ℹ️  You can create it with: CREATE DATABASE atenda;")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
