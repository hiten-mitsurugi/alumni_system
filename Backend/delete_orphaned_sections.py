import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from survey_app.models import SurveyCategory, SurveyTemplate

# Get all orphaned sections (not linked to any form)
orphaned = SurveyCategory.objects.filter(surveytemplate__isnull=True)

print(f"Found {orphaned.count()} orphaned sections:")
for cat in orphaned:
    print(f"  - {cat.name} (ID: {cat.id})")

if orphaned.count() > 0:
    response = input("\nDelete all orphaned sections? (yes/no): ")
    if response.lower() == 'yes':
        count = orphaned.count()
        orphaned.delete()
        print(f"✅ Deleted {count} orphaned sections")
        print("\nNow you can create new sections in the frontend and they will be properly linked!")
    else:
        print("Operation cancelled")
else:
    print("\nNo orphaned sections found!")
