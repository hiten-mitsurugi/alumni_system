"""
Django management command to test the simplified WorkHistory functionality.
Usage: python manage.py test_work_history
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from auth_app.models import WorkHistory, Profile
from auth_app.serializers import WorkHistorySerializer

class Command(BaseCommand):
    help = 'Test the simplified WorkHistory functionality'

    def handle(self, *args, **options):
        self.stdout.write("🧪 Testing Simplified Work History Functionality")
        self.stdout.write("=" * 50)
        
        User = get_user_model()
        
        # Create or get test user
        user, created = User.objects.get_or_create(
            username='test_experience_user',
            defaults={
                'email': 'test_exp@example.com',
                'first_name': 'Test',
                'last_name': 'Experience',
                'is_approved': True
            }
        )
        
        if created:
            user.set_password('testpass123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f"✅ Created test user: {user.username}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"✅ Using existing test user: {user.username}"))
        
        # Clear existing work history
        WorkHistory.objects.filter(user=user).delete()
        
        # Test 1: Create work history
        self.stdout.write("\n1️⃣ Creating work history with simplified fields...")
        
        work_data = {
            'user': user,
            'occupation': 'Software Engineer',
            'employing_agency': 'Tech Company Inc.',
            'classification': 'private',
            'start_date': '2022-01-15',
            'end_date': '2023-12-31',
            'length_of_service': '2 years',
            'description': 'Developed web applications using Django and Vue.js. Led team of 3 developers.',
            'is_current_job': False
        }
        
        work_history = WorkHistory.objects.create(**work_data)
        self.stdout.write(self.style.SUCCESS(f"✅ Created: {work_history}"))
        
        # Test 2: Create current job
        self.stdout.write("\n2️⃣ Creating current job...")
        
        current_job_data = {
            'user': user,
            'occupation': 'Senior Software Engineer',
            'employing_agency': 'Future Tech Corp',
            'classification': 'private',
            'start_date': '2024-01-01',
            'end_date': None,
            'length_of_service': '10 months',
            'description': 'Leading backend architecture and mentoring junior developers.',
            'is_current_job': True
        }
        
        current_job = WorkHistory.objects.create(**current_job_data)
        self.stdout.write(self.style.SUCCESS(f"✅ Created current job: {current_job}"))
        
        # Test 3: Test serialization
        self.stdout.write("\n3️⃣ Testing serialization...")
        
        serializer = WorkHistorySerializer(work_history)
        data = serializer.data
        
        expected_fields = [
            'id', 'occupation', 'employing_agency', 'classification',
            'start_date', 'end_date', 'length_of_service', 'description',
            'is_current_job', 'skills'
        ]
        
        for field in expected_fields:
            if field in data:
                self.stdout.write(f"   ✓ {field}: {data[field]}")
            else:
                self.stdout.write(self.style.ERROR(f"   ❌ Missing field: {field}"))
        
        # Test 4: Test current job query
        self.stdout.write("\n4️⃣ Testing current job query...")
        
        current_jobs = WorkHistory.objects.filter(user=user, is_current_job=True)
        self.stdout.write(self.style.SUCCESS(f"✅ Found {current_jobs.count()} current job(s)"))
        
        # Test 5: Test Profile integration
        self.stdout.write("\n5️⃣ Testing Profile integration...")
        
        try:
            profile, created = Profile.objects.get_or_create(user=user)
            profile.save()  # This should update employment info
            
            self.stdout.write(self.style.SUCCESS("✅ Profile updated successfully"))
            self.stdout.write(f"   - Present occupation: {profile.present_occupation}")
            self.stdout.write(f"   - Employment classification: {profile.employment_classification}")
            self.stdout.write(f"   - Employing agency: {profile.employing_agency}")
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Profile error: {e}"))
        
        # Test 6: Verify field removal
        self.stdout.write("\n6️⃣ Verifying removed fields...")
        
        removed_fields = [
            'job_type', 'employment_status', 'how_got_job',
            'monthly_income', 'is_breadwinner', 'college_education_relevant'
        ]
        
        for field in removed_fields:
            if hasattr(WorkHistory, field):
                self.stdout.write(self.style.ERROR(f"   ❌ {field} still exists"))
            else:
                self.stdout.write(self.style.SUCCESS(f"   ✅ {field} removed"))
        
        # Summary
        total_work = WorkHistory.objects.filter(user=user).count()
        current_count = WorkHistory.objects.filter(user=user, is_current_job=True).count()
        
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS("🎉 Test Complete!"))
        self.stdout.write(f"📊 Total work histories: {total_work}")
        self.stdout.write(f"📊 Current jobs: {current_count}")
        
        # Test simplified field creation via dictionary (like from API)
        self.stdout.write("\n7️⃣ Testing API-style data creation...")
        
        api_style_data = {
            'occupation': 'DevOps Engineer',
            'employing_agency': 'Cloud Solutions Ltd.',
            'classification': 'private',
            'start_date': '2021-06-01',
            'end_date': '2021-12-31',
            'length_of_service': '6 months',
            'description': 'Managed CI/CD pipelines and cloud infrastructure.',
            'is_current_job': False
        }
        
        # Test serializer validation and creation
        serializer = WorkHistorySerializer(data=api_style_data)
        if serializer.is_valid():
            # Save with user (serializer excludes user field)
            work_instance = serializer.save(user=user)
            self.stdout.write(self.style.SUCCESS(f"✅ API-style creation successful: {work_instance}"))
        else:
            self.stdout.write(self.style.ERROR(f"❌ Serializer validation failed: {serializer.errors}"))