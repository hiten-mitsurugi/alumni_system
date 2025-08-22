from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from survey_app.models import SurveyCategory, SurveyQuestion

User = get_user_model()


class Command(BaseCommand):
    help = 'Populate the database with Alumni Tracer Survey questions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@example.com',
            help='Email of the admin user who will be set as creator'
        )

    def handle(self, *args, **options):
        admin_email = options['admin_email']
        
        # Get or create admin user
        try:
            admin_user = User.objects.filter(user_type__in=[1, 2]).first()
            if not admin_user:
                self.stdout.write(
                    self.style.WARNING('No admin user found. Creating default admin...')
                )
                admin_user = User.objects.create_user(
                    username='admin',
                    email=admin_email,
                    password='admin123',
                    user_type=1,
                    first_name='System',
                    last_name='Administrator',
                    is_approved=True
                )
                self.stdout.write(
                    self.style.SUCCESS(f'Created admin user: {admin_email}')
                )
            else:
                self.stdout.write(
                    self.style.SUCCESS(f'Using existing admin: {admin_user.email}')
                )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error getting admin user: {e}')
            )
            return

        # Survey data structure (based on Prens' implementation)
        survey_data = {
            'Personal Information': {
                'order': 1,
                'description': 'Basic personal and demographic information',
                'questions': [
                    {
                        'question_text': 'What is your current civil status?',
                        'question_type': 'radio',
                        'options': ['Single', 'Married', 'Separated', 'Widowed'],
                        'is_required': True,
                        'order': 1
                    },
                    {
                        'question_text': 'What is your current employment status?',
                        'question_type': 'radio',
                        'options': [
                            'Employed Locally',
                            'Employed Internationally', 
                            'Self-Employed',
                            'Unemployed',
                            'Retired'
                        ],
                        'is_required': True,
                        'order': 2
                    },
                    {
                        'question_text': 'Please specify your current location/address',
                        'question_type': 'textarea',
                        'is_required': True,
                        'order': 3
                    }
                ]
            },
            'Educational Background': {
                'order': 2,
                'description': 'Information about educational background and experiences',
                'questions': [
                    {
                        'question_text': 'What program did you graduate from?',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 1
                    },
                    {
                        'question_text': 'What year did you graduate?',
                        'question_type': 'number',
                        'min_value': 1990,
                        'max_value': 2030,
                        'is_required': True,
                        'order': 2
                    },
                    {
                        'question_text': 'How would you rate the relevance of your college education to your current job?',
                        'question_type': 'radio',
                        'options': ['Very Relevant', 'Relevant', 'Somewhat Relevant', 'Not Relevant'],
                        'is_required': True,
                        'order': 3
                    },
                    {
                        'question_text': 'Have you pursued further studies after graduation?',
                        'question_type': 'yes_no',
                        'is_required': True,
                        'order': 4
                    }
                ]
            },
            'Employment History': {
                'order': 3,
                'description': 'Current and previous employment information',
                'questions': [
                    {
                        'question_text': 'What is your current occupation/job title?',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 1
                    },
                    {
                        'question_text': 'What type of organization do you work for?',
                        'question_type': 'radio',
                        'options': ['Government', 'Private', 'NGO', 'Freelance', 'Business Owner'],
                        'is_required': True,
                        'order': 2
                    },
                    {
                        'question_text': 'What is your monthly income range?',
                        'question_type': 'radio',
                        'options': [
                            'Less than P15,000',
                            'P15,000 - P29,999',
                            'P30,000 - P49,999',
                            'P50,000 and above',
                            'Prefer not to say'
                        ],
                        'is_required': False,
                        'order': 3
                    },
                    {
                        'question_text': 'How long have you been in your current position?',
                        'question_type': 'text',
                        'placeholder_text': 'e.g., 2 years, 6 months',
                        'is_required': True,
                        'order': 4
                    },
                    {
                        'question_text': 'Are you the primary breadwinner in your family?',
                        'question_type': 'yes_no',
                        'is_required': True,
                        'order': 5
                    }
                ]
            },
            'Skills Assessment': {
                'order': 4,
                'description': 'Assessment of skills and competencies',
                'questions': [
                    {
                        'question_text': 'Rate your critical thinking and problem-solving skills',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'help_text': '1 = Poor, 5 = Excellent',
                        'is_required': True,
                        'order': 1
                    },
                    {
                        'question_text': 'Rate your communication skills',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'help_text': '1 = Poor, 5 = Excellent',
                        'is_required': True,
                        'order': 2
                    },
                    {
                        'question_text': 'Rate your leadership and teamwork abilities',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'help_text': '1 = Poor, 5 = Excellent',
                        'is_required': True,
                        'order': 3
                    },
                    {
                        'question_text': 'Rate your innovation and creativity skills',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'help_text': '1 = Poor, 5 = Excellent',
                        'is_required': True,
                        'order': 4
                    },
                    {
                        'question_text': 'Rate your adaptability to change',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'help_text': '1 = Poor, 5 = Excellent',
                        'is_required': True,
                        'order': 5
                    }
                ]
            },
            'Curriculum Feedback': {
                'order': 5,
                'description': 'Feedback on curriculum and program relevance',
                'questions': [
                    {
                        'question_text': 'How would you rate the relevance of General Education subjects?',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'help_text': '1 = Not Relevant, 5 = Very Relevant',
                        'is_required': True,
                        'order': 1
                    },
                    {
                        'question_text': 'How would you rate the relevance of Core/Major subjects?',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'help_text': '1 = Not Relevant, 5 = Very Relevant',
                        'is_required': True,
                        'order': 2
                    },
                    {
                        'question_text': 'How would you rate the relevance of Internship/OJT experience?',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'help_text': '1 = Not Relevant, 5 = Very Relevant',
                        'is_required': True,
                        'order': 3
                    },
                    {
                        'question_text': 'How would you rate the relevance of Elective subjects?',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'help_text': '1 = Not Relevant, 5 = Very Relevant',
                        'is_required': True,
                        'order': 4
                    }
                ]
            },
            'Further Studies': {
                'order': 6,
                'description': 'Information about further education and studies',
                'questions': [
                    {
                        'question_text': 'If you pursued further studies, what level?',
                        'question_type': 'radio',
                        'options': ["Master's Degree", 'Doctoral Degree', 'Certificate Course', 'Not Applicable'],
                        'is_required': False,
                        'order': 1
                    },
                    {
                        'question_text': 'What field of study did you pursue?',
                        'question_type': 'text',
                        'is_required': False,
                        'order': 2
                    },
                    {
                        'question_text': 'Was your further study related to your undergraduate program?',
                        'question_type': 'yes_no',
                        'is_required': False,
                        'order': 3
                    },
                    {
                        'question_text': 'What motivated you to pursue further studies?',
                        'question_type': 'textarea',
                        'is_required': False,
                        'order': 4
                    }
                ]
            },
            'Feedback and Suggestions': {
                'order': 7,
                'description': 'General feedback and recommendations',
                'questions': [
                    {
                        'question_text': 'What recommendations would you give to improve the curriculum?',
                        'question_type': 'textarea',
                        'is_required': False,
                        'order': 1
                    },
                    {
                        'question_text': 'What additional skills should the university focus on developing?',
                        'question_type': 'textarea',
                        'is_required': False,
                        'order': 2
                    },
                    {
                        'question_text': 'How can the university better prepare students for the job market?',
                        'question_type': 'textarea',
                        'is_required': False,
                        'order': 3
                    },
                    {
                        'question_text': 'Overall, how would you rate your university experience?',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'help_text': '1 = Poor, 5 = Excellent',
                        'is_required': True,
                        'order': 4
                    }
                ]
            }
        }

        # Create categories and questions
        created_categories = 0
        created_questions = 0

        for category_name, category_data in survey_data.items():
            # Create or get category
            category, created = SurveyCategory.objects.get_or_create(
                name=category_name,
                defaults={
                    'description': category_data['description'],
                    'order': category_data['order'],
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            
            if created:
                created_categories += 1
                self.stdout.write(f'Created category: {category_name}')
            else:
                self.stdout.write(f'Category already exists: {category_name}')

            # Create questions for this category
            for question_data in category_data['questions']:
                question, created = SurveyQuestion.objects.get_or_create(
                    category=category,
                    question_text=question_data['question_text'],
                    defaults={
                        'question_type': question_data['question_type'],
                        'options': question_data.get('options', None),
                        'is_required': question_data.get('is_required', False),
                        'min_value': question_data.get('min_value', None),
                        'max_value': question_data.get('max_value', None),
                        'max_length': question_data.get('max_length', None),
                        'placeholder_text': question_data.get('placeholder_text', ''),
                        'help_text': question_data.get('help_text', ''),
                        'order': question_data.get('order', 0),
                        'is_active': True,
                        'created_by': admin_user
                    }
                )
                
                if created:
                    created_questions += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully populated survey data:\n'
                f'- Created {created_categories} new categories\n'
                f'- Created {created_questions} new questions\n'
                f'- Total categories: {SurveyCategory.objects.count()}\n'
                f'- Total questions: {SurveyQuestion.objects.count()}'
            )
        )
