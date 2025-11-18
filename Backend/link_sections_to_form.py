import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from survey_app.models import SurveyTemplate, SurveyCategory

# Get the form
form = SurveyTemplate.objects.get(id=2)
print(f"Form: {form.name}")

# Get all orphaned sections
orphaned = SurveyCategory.objects.filter(surveytemplates__isnull=True)
print(f"\nFound {orphaned.count()} orphaned sections:")
for cat in orphaned:
    print(f"  - {cat.name} (ID: {cat.id})")

# Ask for confirmation
response = input("\nDo you want to link ALL these sections to the form? (yes/no): ")

if response.lower() == 'yes':
    for cat in orphaned:
        form.categories.add(cat)
        print(f"✅ Linked: {cat.name}")
    
    print(f"\n✅ Done! Form now has {form.categories.count()} sections")
    for cat in form.categories.all().order_by('order', 'name'):
        print(f"  - {cat.name}")
else:
    print("Operation cancelled")
