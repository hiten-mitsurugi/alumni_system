#!/usr/bin/env python
"""
TRACE EXACT ERROR LOCATION
Add detailed tracing to find WHERE is_current_job is being accessed
"""
import os
import sys
import django
import json
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')

# PATCH: Trace all database queries
from django.db import connection
from django.test.utils import CaptureQueriesContext

django.setup()

from django.test import Client
from auth_app.models import CustomUser
from django.core.files.uploadedfile import SimpleUploadedFile

print("\n" + "="*80)
print("TRACE EXACT ERROR - WHERE IS is_current_job ACCESSED?")
print("="*80)

client = Client()

# Clean up
test_email = "trace_test@test.com"
CustomUser.objects.filter(email=test_email).delete()

# Mock files
png_data = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01'
    b'\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
)

profile_picture = SimpleUploadedFile("trace_test.png", png_data, content_type="image/png")
government_id = SimpleUploadedFile("trace_test.pdf", b"%PDF\n", content_type="application/pdf")

form_data = {
    'first_name': 'Trace',
    'middle_name': '',
    'last_name': 'Test',
    'email': test_email,
    'contact_number': '+63-9171234567',
    'password': 'TestPass123!',
    'confirm_password': 'TestPass123!',
    'program': 'BS IT',
    'present_address_data': json.dumps({'address_type': 'philippines', 'region_name': 'Caraga', 'province_name': 'Agusan Del Norte', 'city_name': 'Butuan', 'barangay': 'Agao', 'street_address': 'Main St', 'postal_code': '8600', 'country': '', 'full_address': ''}),
    'permanent_address_data': json.dumps({'address_type': 'philippines', 'region_name': 'Caraga', 'province_name': 'Agusan Del Norte', 'city_name': 'Butuan', 'barangay': 'Agao', 'street_address': 'Main St', 'postal_code': '8600', 'country': '', 'full_address': ''}),
    'birth_date': '1995-05-15',
    'year_graduated': '2015',
    'employment_status': 'employed_locally',
    'gender': 'male',
    'civil_status': 'married',
    'mothers_name': 'Mom',
    'mothers_occupation': 'Teacher',
    'fathers_name': 'Dad',
    'fathers_occupation': 'Engineer',
    'alumni_exists': 'true',
    'survey_responses': json.dumps([{'question': 225, 'response_data': True}]),
}

print("\nCapturing all SQL queries during registration...")
print("-" * 80)

try:
    # Capture queries
    with CaptureQueriesContext(connection) as ctx:
        response = client.post(
            '/api/auth/register/',
            {**form_data, 'government_id': government_id, 'profile_picture': profile_picture},
            format='multipart'
        )
    
    print(f"\nTotal queries executed: {len(ctx)}")
    print(f"Response status: {response.status_code}")
    
    if response.status_code != 201:
        print(f"\nERROR - Status {response.status_code}")
        print(f"Response: {response.json()}")
    else:
        print(f"\nSUCCESS - User created!")
    
    # Show all queries
    print("\n" + "-"*80)
    print("QUERIES EXECUTED (looking for is_current_job):")
    print("-"*80)
    
    for i, query in enumerate(ctx.captured_queries, 1):
        sql = query['sql']
        
        # Highlight problematic queries
        if 'is_current_job' in sql.lower():
            print(f"\n❌ QUERY {i} - CONTAINS is_current_job:")
            print(f"   {sql[:200]}...")
        elif 'work_history' in sql.lower():
            print(f"\n⚠️  QUERY {i} - WORK_HISTORY table:")
            print(f"   {sql[:200]}...")
        # Show CREATE/INSERT queries
        elif 'INSERT' in sql or 'CREATE' in sql:
            print(f"\n✅ QUERY {i} - {sql.split()[0:3]}:")
            print(f"   {sql[:150]}...")
    
except Exception as e:
    print(f"\n❌ EXCEPTION: {e}")
    traceback.print_exc()
