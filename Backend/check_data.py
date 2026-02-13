import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from survey_app.models import SurveyCategory, SurveyQuestion, SurveyTemplate

print('=== CATEGORIES IN DATABASE ===')
categories = SurveyCategory.objects.all().order_by('id')
for cat in categories:
    questions_count = SurveyQuestion.objects.filter(category=cat).count()
    print(f'ID: {cat.id}, Name: "{cat.name}", Active: {cat.is_active}, Questions: {questions_count}')

print(f'\nTotal categories: {categories.count()}')

print('\n=== ALL QUESTIONS ===')
questions = SurveyQuestion.objects.all().order_by('id')
print(f'Total questions in database: {questions.count()}')

if questions.count() > 0:
    print('\nFirst 20 questions:')
    for q in questions[:20]:
        cat_name = q.category.name if q.category else 'NO CATEGORY'
        print(f'  Q{q.id}: "{q.question_text[:60]}..." -> Category: {cat_name} (ID: {q.category_id})')

print('\n=== TEMPLATE 1 LINKED CATEGORIES ===')
try:
    template = SurveyTemplate.objects.get(id=1)
    linked_cats = template.categories.all()
    print(f'Categories currently linked to template "{template.name}": {linked_cats.count()}')
    for c in linked_cats:
        print(f'  - {c.name} (ID: {c.id})')
except SurveyTemplate.DoesNotExist:
    print('Template 1 does not exist')

print('\n=== RECOVERY INFORMATION ===')
orphaned_categories = []
for cat in categories:
    if not template.categories.filter(id=cat.id).exists():
        questions_count = SurveyQuestion.objects.filter(category=cat).count()
        if questions_count > 0:
            orphaned_categories.append((cat, questions_count))
            print(f'ORPHANED: Category "{cat.name}" (ID: {cat.id}) has {questions_count} questions but is NOT linked to template')

if orphaned_categories:
    print(f'\n⚠️  Found {len(orphaned_categories)} orphaned categories with questions!')
    print('These can be recovered by re-linking them to the template.')
else:
    print('\n✅ No orphaned categories found.')
