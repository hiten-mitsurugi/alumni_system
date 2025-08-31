from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from survey_app.models import SurveyCategory, SurveyQuestion

User = get_user_model()

class Command(BaseCommand):
    help = 'Update registration survey categories and questions with comprehensive list'

    def handle(self, *args, **options):
        # Get admin user
        admin_user = User.objects.filter(user_type=1).first()
        if not admin_user:
            self.stdout.write("No admin user found. Run create_admin_accounts first.")
            return

        # Clear existing questions for specific categories only
        self.stdout.write("Clearing existing survey questions for Work History, Curriculum, and Perception categories...")
        SurveyQuestion.objects.filter(category__name__in=[
            'Work History', 'Curriculum Relevance Assessment', 'Perception & Further Studies'
        ]).delete()

        # Recreate Work History with comprehensive questions
        work_category = SurveyCategory.objects.get(name='Work History')
        
        # Present Employment Section
        present_employment_questions = [
            {
                'question_text': 'Are you presently employed?',
                'question_type': 'radio',
                'options': ['Yes', 'No', 'Never been employed'],
                'is_required': True,
                'order': 1
            },
            {
                'question_text': 'Present Employment Status',
                'question_type': 'radio',
                'options': ['Employed Locally', 'Employed Internationally', 'Self-employed', 'Unemployed', 'Retired'],
                'is_required': True,
                'order': 2
            },
            {
                'question_text': 'Classification of Employment / Sector',
                'question_type': 'radio',
                'options': ['Government', 'Private', 'NGO', 'Freelance', 'Business Owner'],
                'is_required': True,
                'order': 3
            },
            {
                'question_text': 'Present Occupation',
                'question_type': 'text',
                'is_required': True,
                'order': 4,
                'placeholder_text': 'Enter your current job title/occupation'
            },
            {
                'question_text': 'Employing Agency Name & Location',
                'question_type': 'text',
                'is_required': True,
                'order': 5,
                'placeholder_text': 'Company name and location'
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
            # First Job Section
            {
                'question_text': 'Is your current job your first job?',
                'question_type': 'yes_no',
                'is_required': True,
                'order': 12
            },
            {
                'question_text': 'First Job Title',
                'question_type': 'text',
                'is_required': False,
                'order': 13,
                'placeholder_text': 'Enter your first job title (if different from current)',
                'help_text': 'Only answer if your current job is not your first job'
            },
            {
                'question_text': 'First Employer',
                'question_type': 'text',
                'is_required': False,
                'order': 14,
                'placeholder_text': 'Enter your first employer name',
                'help_text': 'Only answer if your current job is not your first job'
            },
            {
                'question_text': 'Employment Status in First Job',
                'question_type': 'radio',
                'options': ['Employed Locally', 'Employed Internationally', 'Self-employed'],
                'is_required': False,
                'order': 15,
                'help_text': 'Only answer if your current job is not your first job'
            },
            {
                'question_text': 'Sector Classification (First Job)',
                'question_type': 'radio',
                'options': ['Government', 'Private', 'NGO', 'Freelance', 'Business Owner'],
                'is_required': False,
                'order': 16,
                'help_text': 'Only answer if your current job is not your first job'
            },
            {
                'question_text': 'How did you get your first job?',
                'question_type': 'radio',
                'options': ['Job posting/Advertisement', 'Referral from friends/family', 'Company recruitment', 'Walk-in application', 'Online job portal', 'Social media', 'Other'],
                'is_required': False,
                'order': 17,
                'help_text': 'Only answer if your current job is not your first job'
            },
            {
                'question_text': 'Monthly Income in First Job',
                'question_type': 'radio',
                'options': ['Less than ₱15,000', '₱15,000–₱29,999', '₱30,000–₱49,999', '₱50,000 and above', 'Prefer not to say'],
                'is_required': False,
                'order': 18,
                'help_text': 'Only answer if your current job is not your first job'
            },
            {
                'question_text': 'Length of Service in First Job (Years)',
                'question_type': 'number',
                'is_required': False,
                'order': 19,
                'min_value': 0,
                'max_value': 50,
                'placeholder_text': 'Number of years',
                'help_text': 'Only answer if your current job is not your first job'
            },
            {
                'question_text': 'Length of Service in First Job (Months)',
                'question_type': 'number',
                'is_required': False,
                'order': 20,
                'min_value': 0,
                'max_value': 11,
                'placeholder_text': 'Additional months',
                'help_text': 'Only answer if your current job is not your first job'
            },
            {
                'question_text': 'Was college education relevant to first job?',
                'question_type': 'radio',
                'options': ['Yes', 'No', 'Somewhat'],
                'is_required': False,
                'order': 21,
                'help_text': 'Only answer if your current job is not your first job'
            }
        ]

        for q_data in present_employment_questions:
            question, created = SurveyQuestion.objects.get_or_create(
                category=work_category,
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
                self.stdout.write(f"Created work question: {q_data['question_text'][:50]}...")

        # Skills Relevance Assessment - Recreate if missing
        skills_category = SurveyCategory.objects.get(name='Skills Relevance Assessment')
        
        # Check if skills questions exist, if not create them
        if SurveyQuestion.objects.filter(category=skills_category).count() == 0:
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

        # Curriculum Relevance Assessment - Update to match exact requirements
        curriculum_category = SurveyCategory.objects.get(name='Curriculum Relevance Assessment')
        
        # Clear existing curriculum questions to rebuild
        SurveyQuestion.objects.filter(category=curriculum_category).delete()
        
        curriculum_items = [
            'General Education / Minor Courses',
            'Core / Major Courses', 
            'Special Professional Courses',
            'Electives',
            'Internship / OJT',
            'Co-Curricular Activities (seminars, field trips)',
            'Extra-Curricular Activities (intramurals, exit conference)'
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

        # Perception & Further Studies - Expand with detailed questions
        perception_category = SurveyCategory.objects.get(name='Perception & Further Studies')
        
        # Clear existing perception questions to rebuild
        SurveyQuestion.objects.filter(category=perception_category).delete()
        
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
            },
            {
                'question_text': 'Mode of Study',
                'question_type': 'radio',
                'options': ['Full-time', 'Part-time', 'Online', 'Others'],
                'is_required': False,
                'order': 3,
                'help_text': 'Only answer if you pursued further studies'
            },
            {
                'question_text': 'Level of Study',
                'question_type': 'radio',
                'options': ['Master\'s', 'Doctoral', 'Certificate', 'Professional Course'],
                'is_required': False,
                'order': 4,
                'help_text': 'Only answer if you pursued further studies'
            },
            {
                'question_text': 'Field of Study',
                'question_type': 'text',
                'is_required': False,
                'order': 5,
                'placeholder_text': 'Enter the field/discipline of your further studies',
                'help_text': 'Only answer if you pursued further studies'
            },
            {
                'question_text': 'Specialization',
                'question_type': 'text',
                'is_required': False,
                'order': 6,
                'placeholder_text': 'Enter your specialization',
                'help_text': 'Only answer if you pursued further studies'
            },
            {
                'question_text': 'Is it related to your undergraduate degree?',
                'question_type': 'yes_no',
                'is_required': False,
                'order': 7,
                'help_text': 'Only answer if you pursued further studies'
            },
            {
                'question_text': 'Reasons for further study',
                'question_type': 'checkbox',
                'options': ['Career growth', 'Interest', 'Job requirement', 'Promotion', 'Personal development', 'Others'],
                'is_required': False,
                'order': 8,
                'help_text': 'Select all that apply. Only answer if you pursued further studies'
            }
        ]

        for q_data in perception_questions:
            question, created = SurveyQuestion.objects.get_or_create(
                category=perception_category,
                question_text=q_data['question_text'],
                defaults={
                    'question_type': q_data['question_type'],
                    'options': q_data.get('options', []),
                    'min_value': q_data.get('min_value'),
                    'max_value': q_data.get('max_value'),
                    'is_required': q_data['is_required'],
                    'order': q_data['order'],
                    'placeholder_text': q_data.get('placeholder_text', ''),
                    'help_text': q_data.get('help_text', ''),
                    'is_active': True,
                    'created_by': admin_user
                }
            )
            if created:
                self.stdout.write(f"Created perception question: {q_data['question_text'][:50]}...")

        # Feedback & Recommendations - Recreate if missing
        feedback_category = SurveyCategory.objects.get(name='Feedback & Recommendations')
        
        # Check if feedback question exists, if not create it
        if SurveyQuestion.objects.filter(category=feedback_category).count() == 0:
            feedback_question, created = SurveyQuestion.objects.get_or_create(
                category=feedback_category,
                question_text='What are your recommendations to improve the program you had in college?',
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

        self.stdout.write(self.style.SUCCESS('Successfully updated registration survey structure with comprehensive questions'))
        
        # Print summary
        categories = SurveyCategory.objects.filter(name__in=[
            'Work History', 'Skills Relevance Assessment', 'Curriculum Relevance Assessment',
            'Perception & Further Studies', 'Feedback & Recommendations'
        ])
        
        self.stdout.write("\nSummary:")
        for cat in categories:
            count = SurveyQuestion.objects.filter(category=cat).count()
            self.stdout.write(f"- {cat.name}: {count} questions")
