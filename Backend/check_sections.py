import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from survey_app.models import SurveyTemplate, SurveyCategory, SurveyTemplateCategory

print("\n=== ALL FORMS ===")
for form in SurveyTemplate.objects.all():
    print(f"ID: {form.id} | Name: {form.name}")
    linked_categories = form.categories.all()
    print(f"  Linked sections: {linked_categories.count()}")
    for cat in linked_categories:
        print(f"    - {cat.name} (ID: {cat.id}, Order: {cat.order})")

print("\n=== ALL SECTIONS (SurveyCategory) ===")
for cat in SurveyCategory.objects.all().order_by('id'):
    print(f"ID: {cat.id} | Name: {cat.name} | Order: {cat.order}")
    # Check which forms this category is linked to
    linked_forms = SurveyTemplate.objects.filter(categories=cat)
    if linked_forms.exists():
        print(f"  Linked to forms: {[f.name for f in linked_forms]}")
    else:
        print(f"  ⚠️ Not linked to any form!")

print("\n=== JUNCTION TABLE (SurveyTemplateCategory) ===")
for link in SurveyTemplateCategory.objects.all():
    print(f"Form: {link.template.name} (ID: {link.template_id}) <-> Section: {link.category.name} (ID: {link.category_id})")
