from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from survey_app.models import SurveyCategory, SurveyQuestion

User = get_user_model()

class Command(BaseCommand):
    help = 'Setup conditional logic for Work History questions'

    def handle(self, *args, **options):
        # Get admin user
        admin_user = User.objects.filter(user_type=1).first()
        if not admin_user:
            self.stdout.write("No admin user found. Run create_admin_accounts first.")
            return

        try:
            work_category = SurveyCategory.objects.get(name='Work History')
        except SurveyCategory.DoesNotExist:
            self.stdout.write("Work History category not found. Run update_registration_surveys first.")
            return

        # Find the "Is your current job your first job?" question
        try:
            trigger_question = SurveyQuestion.objects.get(
                category=work_category,
                question_text="Is your current job your first job?"
            )
        except SurveyQuestion.DoesNotExist:
            self.stdout.write("Trigger question not found.")
            return

        # Define the conditional questions that should only appear if user answers "No" (false)
        conditional_question_texts = [
            "First Job Title",
            "First Employer", 
            "Employment Status in First Job",
            "Sector Classification (First Job)",
            "How did you get your first job?",
            "Monthly Income in First Job",
            "Length of Service in First Job (Years)",
            "Length of Service in First Job (Months)",
            "Was college education relevant to first job?"
        ]

        updated_count = 0
        for question_text in conditional_question_texts:
            try:
                question = SurveyQuestion.objects.get(
                    category=work_category,
                    question_text=question_text
                )
                
                # Update the question to depend on the trigger question
                question.depends_on_question = trigger_question
                question.depends_on_value = "false"  # Show when user answers "No" 
                question.is_required = False  # Make conditional questions non-required
                question.save()
                
                updated_count += 1
                self.stdout.write(f"Updated conditional logic for: {question_text}")
                
            except SurveyQuestion.DoesNotExist:
                self.stdout.write(f"Question not found: {question_text}")

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully set up conditional logic for {updated_count} Work History questions'
            )
        )
        
        # Display summary
        self.stdout.write("\nConditional Logic Summary:")
        self.stdout.write(f"Trigger Question: {trigger_question.question_text}")
        self.stdout.write(f"Trigger Value: No (false)")
        self.stdout.write(f"Dependent Questions: {updated_count}")
        
        # Show all conditional questions
        conditional_questions = SurveyQuestion.objects.filter(
            category=work_category,
            depends_on_question=trigger_question
        ).order_by('order')
        
        self.stdout.write("\nConditional Questions:")
        for q in conditional_questions:
            self.stdout.write(f"- {q.question_text}")
