from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from survey_app.models import SurveyCategory, SurveyQuestion

User = get_user_model()

class Command(BaseCommand):
    help = 'Create registration survey categories and questions'

    def handle(self, *args, **options):
        # Get or create a super admin user to assign as creator
        try:
            admin_user = User.objects.filter(user_type=1).first()
            if not admin_user:
                admin_user = User.objects.create_user(
                    username='system_admin',
                    email='admin@system.com',
                    password='TempPassword123!',
                    first_name='System',
                    last_name='Admin',
                    user_type=1
                )
        except Exception as e:
            self.stdout.write(f"Error creating admin user: {e}")
            return

        # Create Registration Survey Categories
        categories_data = [
            {
                'name': 'Work History',
                'description': 'Current and previous employment information',
                'order': 1
            },
            {
                'name': 'Skills Relevance Assessment',
                'description': 'Rate the relevance of skills learned in your workplace',
                'order': 2
            },
            {
                'name': 'Curriculum Relevance Assessment',
                'description': 'Rate the usefulness of your college curriculum',
                'order': 3
            },
            {
                'name': 'Perception & Further Studies',
                'description': 'Your views on competitiveness and continuing education',
                'order': 4
            },
            {
                'name': 'Feedback & Recommendations',
                'description': 'Your suggestions for program improvement',
                'order': 5
            }
        ]

        for cat_data in categories_data:
            category, created = SurveyCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults={
                    'description': cat_data['description'],
                    'order': cat_data['order'],
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Create Questions for Work History
        work_category = SurveyCategory.objects.get(name='Work History')
        work_questions = [
            {
                'question_text': 'What is your current employment status?',
                'question_type': 'radio',
                'options': ['Employed Locally', 'Employed Internationally', 'Self-Employed', 'Unemployed', 'Retired'],
                'is_required': True,
                'order': 1
            },
            {
                'question_text': 'What is your current occupation/job title?',
                'question_type': 'text',
                'is_required': True,
                'order': 2,
                'placeholder_text': 'Enter your job title'
            },
            {
                'question_text': 'What type of organization do you work for?',
                'question_type': 'radio',
                'options': ['Government', 'Private', 'NGO', 'Freelance', 'Business Owner'],
                'is_required': True,
                'order': 3
            },
            {
                'question_text': 'What is your monthly income range?',
                'question_type': 'radio',
                'options': ['Less than P15,000', 'P15,000 - P29,999', 'P30,000 - P49,999', 'P50,000 and above', 'Prefer not to say'],
                'is_required': True,
                'order': 4
            }
        ]

        for q_data in work_questions:
            question, created = SurveyQuestion.objects.get_or_create(
                category=work_category,
                question_text=q_data['question_text'],
                defaults={
                    'question_type': q_data['question_type'],
                    'options': q_data.get('options', []),
                    'is_required': q_data['is_required'],
                    'order': q_data['order'],
                    'placeholder_text': q_data.get('placeholder_text', ''),
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f"Created work question: {q_data['question_text'][:50]}...")

        # Create Questions for Skills Relevance Category
        skills_category = SurveyCategory.objects.get(name='Skills Relevance Assessment')
        skills_questions = [
            'Critical Thinking',
            'Communication', 
            'Innovation',
            'Collaboration',
            'Leadership',
            'Productivity and Accountability',
            'Entrepreneurship',
            'Global Citizenship',
            'Adaptability',
            'Accessing, Analyzing, and Synthesizing Information'
        ]

        for i, skill in enumerate(skills_questions):
            question, created = SurveyQuestion.objects.get_or_create(
                category=skills_category,
                question_text=f'Rate the relevance of {skill} in your workplace',
                defaults={
                    'question_type': 'rating',
                    'min_value': 1,
                    'max_value': 5,
                    'is_required': True,
                    'order': i + 1,
                    'help_text': '1 = Not Useful, 5 = Very Useful',
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f"Created skills question: {skill}")

        # Create Questions for Curriculum Relevance Category  
        curriculum_category = SurveyCategory.objects.get(name='Curriculum Relevance Assessment')
        curriculum_items = [
            'General Education / Minor Courses',
            'Core / Major Courses', 
            'Special Professional Courses',
            'Electives',
            'Internship / OJT',
            'Co-Curricular Activities',
            'Extra-Curricular Activities'
        ]

        for i, item in enumerate(curriculum_items):
            question, created = SurveyQuestion.objects.get_or_create(
                category=curriculum_category,
                question_text=f'Rate the usefulness of {item} in your professional work',
                defaults={
                    'question_type': 'rating',
                    'min_value': 1,
                    'max_value': 5,
                    'is_required': True,
                    'order': i + 1,
                    'help_text': '1 = Not Useful, 5 = Very Useful',
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f"Created curriculum question: {item}")

        # Create Questions for Perception & Further Studies
        perception_category = SurveyCategory.objects.get(name='Perception & Further Studies')
        perception_questions = [
            {
                'question_text': 'Rate the competitiveness of graduates from your program',
                'question_type': 'rating',
                'min_value': 1,
                'max_value': 5,
                'is_required': True,
                'order': 1,
                'help_text': '1 = Not Competitive, 5 = Very Competitive'
            },
            {
                'question_text': 'Have you pursued further studies after graduation?',
                'question_type': 'yes_no',
                'is_required': True,
                'order': 2
            }
        ]

        for q_data in perception_questions:
            question, created = SurveyQuestion.objects.get_or_create(
                category=perception_category,
                question_text=q_data['question_text'],
                defaults={
                    'question_type': q_data['question_type'],
                    'min_value': q_data.get('min_value'),
                    'max_value': q_data.get('max_value'),
                    'is_required': q_data['is_required'],
                    'order': q_data['order'],
                    'help_text': q_data.get('help_text', ''),
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f"Created perception question: {q_data['question_text'][:50]}...")

        # Create Questions for Feedback & Recommendations
        feedback_category = SurveyCategory.objects.get(name='Feedback & Recommendations')
        feedback_question, created = SurveyQuestion.objects.get_or_create(
            category=feedback_category,
            question_text='What recommendations do you have to improve the program?',
            defaults={
                'question_type': 'textarea',
                'is_required': True,
                'order': 1,
                'placeholder_text': 'Share your suggestions and recommendations...',
                'help_text': 'Your feedback helps us improve our programs',
                'is_active': True,
                'created_by': admin_user
            }
        )
        if created:
            self.stdout.write("Created feedback question")

        self.stdout.write(self.style.SUCCESS('Successfully created registration survey structure'))
