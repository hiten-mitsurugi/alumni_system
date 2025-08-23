from django.core.management.base import BaseCommand
from survey_app.models import SurveyCategory
import json

class Command(BaseCommand):
    help = 'Set up conditional logic for categories'

    def handle(self, *args, **options):
        # Get categories
        employment_status = SurveyCategory.objects.get(name='Employment Status')
        work_history = SurveyCategory.objects.get(name='Work History')
        first_job = SurveyCategory.objects.get(name='First Job')
        perception = SurveyCategory.objects.get(name='Perception')
        further_studies = SurveyCategory.objects.get(name='Further Studies')

        self.stdout.write("Setting up conditional logic...")

        # Work History depends on Employment Status
        work_history.depends_on_category = employment_status
        work_history.depends_on_question_text = 'Are you presently employed?'
        work_history.depends_on_value = json.dumps(['Yes'])
        work_history.save()
        self.stdout.write(f"✓ Work History depends on Employment Status: 'Yes'")

        # First Job depends on Work History
        first_job.depends_on_category = work_history
        first_job.depends_on_question_text = 'Is your current job your first job?'
        first_job.depends_on_value = json.dumps(['No'])
        first_job.save()
        self.stdout.write(f"✓ First Job depends on Work History: 'No'")

        # Further Studies depends on Perception
        further_studies.depends_on_category = perception
        further_studies.depends_on_question_text = 'Have you pursued further studies after graduation?'
        further_studies.depends_on_value = json.dumps(['Yes'])
        further_studies.save()
        self.stdout.write(f"✓ Further Studies depends on Perception: 'Yes'")

        self.stdout.write(self.style.SUCCESS('Successfully set up conditional logic for categories'))

        # Print summary
        self.stdout.write("\nConditional Logic Summary:")
        for cat in SurveyCategory.objects.filter(depends_on_category__isnull=False):
            self.stdout.write(f"• {cat.name} → shows only if '{cat.depends_on_question_text}' = {cat.depends_on_value}")
