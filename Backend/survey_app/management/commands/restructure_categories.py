from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from survey_app.models import SurveyCategory, SurveyQuestion

User = get_user_model()

class Command(BaseCommand):
    help = 'Restructure survey categories with conditional logic'

    def handle(self, *args, **options):
        # Get admin user
        admin_user = User.objects.filter(user_type=1).first()
        if not admin_user:
            self.stdout.write("No admin user found. Run create_admin_accounts first.")
            return

        # Clear existing categories and questions
        self.stdout.write("Clearing existing survey structure...")
        SurveyCategory.objects.filter(name__in=[
            'Work History', 'Skills Relevance Assessment', 'Curriculum Relevance Assessment',
            'Perception & Further Studies', 'Feedback & Recommendations'
        ]).delete()

        # Create new category structure
        categories_data = [
            {
                'name': 'Employment Status',
                'description': 'Current employment verification',
                'order': 1,
                'questions': [
                    {
                        'question_text': 'Are you presently employed?',
                        'question_type': 'radio',
                        'options': ['Yes', 'No', 'Never been employed'],
                        'is_required': True,
                        'order': 1
                    }
                ]
            },
            {
                'name': 'Work History',
                'description': 'Current employment information',
                'order': 2,
                'questions': [
                    {
                        'question_text': 'Present Employment Status',
                        'question_type': 'radio',
                        'options': ['Employed Locally', 'Employed Internationally', 'Self-employed', 'Unemployed', 'Retired'],
                        'is_required': True,
                        'order': 1
                    },
                    {
                        'question_text': 'Classification of Employment / Sector',
                        'question_type': 'radio',
                        'options': ['Government', 'Private', 'NGO', 'Freelance', 'Business Owner'],
                        'is_required': True,
                        'order': 2
                    },
                    {
                        'question_text': 'Present Occupation',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 3,
                        'placeholder_text': 'Enter your current job title/occupation'
                    },
                    {
                        'question_text': 'Employing Agency Name',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 4,
                        'placeholder_text': 'Company/Agency name'
                    },
                    {
                        'question_text': 'Employing Agency Location',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 5,
                        'placeholder_text': 'Location/Address'
                    },
                    {
                        'question_text': 'How did you get your current job?',
                        'question_type': 'radio',
                        'options': ['Job posting/Advertisement', 'Referral from friends/family', 'Company recruitment', 'Walk-in application', 'Online job portal', 'Social media', 'Other'],
                        'is_required': True,
                        'order': 6
                    },
                    {
                        'question_text': 'Monthly Income',
                        'question_type': 'radio',
                        'options': ['Less than ₱15,000', '₱15,000–₱29,999', '₱30,000–₱49,999', '₱50,000 and above', 'Prefer not to say'],
                        'is_required': True,
                        'order': 7
                    },
                    {
                        'question_text': 'Are you the breadwinner?',
                        'question_type': 'yes_no',
                        'is_required': True,
                        'order': 8
                    },
                    {
                        'question_text': 'Length of Service (Years)',
                        'question_type': 'number',
                        'is_required': True,
                        'order': 9,
                        'min_value': 0,
                        'max_value': 50,
                        'placeholder_text': 'Number of years'
                    },
                    {
                        'question_text': 'Length of Service (Months)',
                        'question_type': 'number',
                        'is_required': True,
                        'order': 10,
                        'min_value': 0,
                        'max_value': 11,
                        'placeholder_text': 'Additional months'
                    },
                    {
                        'question_text': 'Was college education relevant to this job?',
                        'question_type': 'radio',
                        'options': ['Yes', 'No', 'Somewhat'],
                        'is_required': True,
                        'order': 11
                    },
                    {
                        'question_text': 'Is your current job your first job?',
                        'question_type': 'yes_no',
                        'is_required': True,
                        'order': 12
                    }
                ]
            },
            {
                'name': 'First Job',
                'description': 'First employment information (if different from current)',
                'order': 3,
                'questions': [
                    {
                        'question_text': 'First Job Title',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 1,
                        'placeholder_text': 'Enter your first job title'
                    },
                    {
                        'question_text': 'First Employer',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 2,
                        'placeholder_text': 'Enter your first employer name'
                    },
                    {
                        'question_text': 'Employment Status in First Job',
                        'question_type': 'radio',
                        'options': ['Employed Locally', 'Employed Internationally', 'Self-employed'],
                        'is_required': True,
                        'order': 3
                    },
                    {
                        'question_text': 'Sector Classification (First Job)',
                        'question_type': 'radio',
                        'options': ['Government', 'Private', 'NGO', 'Freelance', 'Business Owner'],
                        'is_required': True,
                        'order': 4
                    },
                    {
                        'question_text': 'First Job Agency Name',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 5,
                        'placeholder_text': 'Company/Agency name'
                    },
                    {
                        'question_text': 'First Job Agency Location',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 6,
                        'placeholder_text': 'Location/Address'
                    },
                    {
                        'question_text': 'How did you get your first job?',
                        'question_type': 'radio',
                        'options': ['Job posting/Advertisement', 'Referral from friends/family', 'Company recruitment', 'Walk-in application', 'Online job portal', 'Social media', 'Other'],
                        'is_required': True,
                        'order': 7
                    },
                    {
                        'question_text': 'Monthly Income in First Job',
                        'question_type': 'radio',
                        'options': ['Less than ₱15,000', '₱15,000–₱29,999', '₱30,000–₱49,999', '₱50,000 and above', 'Prefer not to say'],
                        'is_required': True,
                        'order': 8
                    },
                    {
                        'question_text': 'Length of Service in First Job (Years)',
                        'question_type': 'number',
                        'is_required': True,
                        'order': 9,
                        'min_value': 0,
                        'max_value': 50,
                        'placeholder_text': 'Number of years'
                    },
                    {
                        'question_text': 'Length of Service in First Job (Months)',
                        'question_type': 'number',
                        'is_required': True,
                        'order': 10,
                        'min_value': 0,
                        'max_value': 11,
                        'placeholder_text': 'Additional months'
                    },
                    {
                        'question_text': 'Was college education relevant to first job?',
                        'question_type': 'radio',
                        'options': ['Yes', 'No', 'Somewhat'],
                        'is_required': True,
                        'order': 11
                    }
                ]
            },
            {
                'name': 'Skills Relevance Assessment',
                'description': 'Rate the relevance of skills learned in your workplace',
                'order': 4,
                'questions': [
                    {
                        'question_text': 'Rate the relevance of Critical Thinking in your workplace',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 1,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the relevance of Communication in your workplace',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 2,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the relevance of Innovation in your workplace',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 3,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the relevance of Collaboration in your workplace',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 4,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the relevance of Leadership in your workplace',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 5,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the relevance of Productivity and Accountability in your workplace',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 6,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the relevance of Entrepreneurship in your workplace',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 7,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the relevance of Global Citizenship in your workplace',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 8,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the relevance of Adaptability in your workplace',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 9,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the relevance of Accessing, Analyzing, and Synthesizing Information in your workplace',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 10,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    }
                ]
            },
            {
                'name': 'Curriculum Relevance Assessment',
                'description': 'Rate the usefulness of your college curriculum',
                'order': 5,
                'questions': [
                    {
                        'question_text': 'Rate the usefulness of General Education / Minor Courses in your professional work',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 1,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the usefulness of Core / Major Courses in your professional work',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 2,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the usefulness of Special Professional Courses in your professional work',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 3,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the usefulness of Electives in your professional work',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 4,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the usefulness of Internship / OJT in your professional work',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 5,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the usefulness of Co-Curricular Activities (seminars, field trips) in your professional work',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 6,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    },
                    {
                        'question_text': 'Rate the usefulness of Extra-Curricular Activities (intramurals, exit conference) in your professional work',
                        'question_type': 'rating',
                        'min_value': 1,
                        'max_value': 5,
                        'is_required': True,
                        'order': 7,
                        'help_text': '1 = Not Useful, 5 = Very Useful'
                    }
                ]
            },
            {
                'name': 'Perception',
                'description': 'Your views on competitiveness and continuing education',
                'order': 6,
                'questions': [
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
            },
            {
                'name': 'Further Studies',
                'description': 'Continuing education information',
                'order': 7,
                'questions': [
                    {
                        'question_text': 'Mode of Study',
                        'question_type': 'radio',
                        'options': ['Full-time', 'Part-time', 'Online', 'Others'],
                        'is_required': True,
                        'order': 1
                    },
                    {
                        'question_text': 'Level of Study',
                        'question_type': 'radio',
                        'options': ['Master\'s', 'Doctoral', 'Certificate', 'Professional Course'],
                        'is_required': True,
                        'order': 2
                    },
                    {
                        'question_text': 'Field of Study',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 3,
                        'placeholder_text': 'Enter the field/discipline of your further studies'
                    },
                    {
                        'question_text': 'Specialization',
                        'question_type': 'text',
                        'is_required': True,
                        'order': 4,
                        'placeholder_text': 'Enter your specialization'
                    },
                    {
                        'question_text': 'Is it related to your undergraduate degree?',
                        'question_type': 'yes_no',
                        'is_required': True,
                        'order': 5
                    },
                    {
                        'question_text': 'Reasons for further study',
                        'question_type': 'checkbox',
                        'options': ['Career growth', 'Interest', 'Job requirement', 'Promotion', 'Personal development', 'Others'],
                        'is_required': True,
                        'order': 6,
                        'help_text': 'Select all that apply'
                    }
                ]
            },
            {
                'name': 'Feedback & Recommendations',
                'description': 'Your suggestions for program improvement',
                'order': 8,
                'questions': [
                    {
                        'question_text': 'What are your recommendations to improve the program you had in college?',
                        'question_type': 'textarea',
                        'is_required': True,
                        'order': 1,
                        'placeholder_text': 'Share your suggestions and recommendations...',
                        'help_text': 'Your feedback helps us improve our programs'
                    }
                ]
            }
        ]

        # Create categories and questions
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

            # Create questions for this category
            for q_data in cat_data['questions']:
                question, created = SurveyQuestion.objects.get_or_create(
                    category=category,
                    question_text=q_data['question_text'],
                    defaults={
                        'question_type': q_data['question_type'],
                        'options': q_data.get('options', []),
                        'is_required': q_data['is_required'],
                        'order': q_data['order'],
                        'placeholder_text': q_data.get('placeholder_text', ''),
                        'help_text': q_data.get('help_text', ''),
                        'min_value': q_data.get('min_value'),
                        'max_value': q_data.get('max_value'),
                        'is_active': True,
                        'created_by': admin_user
                    }
                )
                if created:
                    self.stdout.write(f"  - Created question: {q_data['question_text'][:50]}...")

        self.stdout.write(self.style.SUCCESS('Successfully created new category structure'))
        
        # Print summary
        categories = SurveyCategory.objects.all().order_by('order')
        self.stdout.write("\nCategory Summary:")
        for cat in categories:
            count = SurveyQuestion.objects.filter(category=cat).count()
            self.stdout.write(f"{cat.order}. {cat.name}: {count} questions")
