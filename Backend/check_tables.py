#!/usr/bin/env python
import os
import sys
import django

# Setup Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from django.db import connection

def check_table_exists(table_name):
    cursor = connection.cursor()
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_name = %s
        );
    """, [table_name])
    return cursor.fetchone()[0]

def get_table_structure(table_name):
    cursor = connection.cursor()
    try:
        cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = %s ORDER BY ordinal_position;", [table_name])
        return cursor.fetchall()
    except Exception as e:
        return f"Error: {e}"

print("=== CHECKING DATABASE TABLES ===")

# Check if auth_app_userskill table exists
table_exists = check_table_exists('auth_app_userskill')
print(f"auth_app_userskill table exists: {table_exists}")

if table_exists:
    print("\n=== TABLE STRUCTURE ===")
    structure = get_table_structure('auth_app_userskill')
    for column, data_type in structure:
        print(f"  {column}: {data_type}")

# Also check for privacy related tables
cursor = connection.cursor()
cursor.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public' AND table_name LIKE '%privacy%'
    ORDER BY table_name;
""")
privacy_tables = cursor.fetchall()
print(f"\n=== ALL PRIVACY-RELATED TABLES ===")
for table in privacy_tables:
    print(f"  {table[0]}")

# Check specific tables that might be causing issues
problem_tables = [
    'auth_app_sectionprivacysetting',
    'auth_app_privacyprofile'
]

print(f"\n=== CHECKING PROBLEMATIC TABLES ===")
for table_name in problem_tables:
    exists = check_table_exists(table_name)
    print(f"{table_name}: {'EXISTS' if exists else 'NOT FOUND'}")