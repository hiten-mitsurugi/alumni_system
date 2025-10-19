from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from survey_app.models import SurveyCategory, SurveyQuestion

User = get_user_model()


class Command(BaseCommand):
    help = 'Create Alumni Tracer Survey Questions based on the provided structure'

    def handle(self, *args, **options):
        # Get or create super admin user
        super_admin = User.objects.filter(user_type=1).first()
        if not super_admin:
            super_admin = User.objects.create_user(
                username='admin',
                email='admin@example.com',
                password='admin123',
                user_type=1
            )

        # Clear existing data
        self.stdout.write('Clearing existing survey data...')
        SurveyQuestion.objects.all().delete()
        SurveyCategory.objects.all().delete()

        # Create categories
        categories_data = [
            {
                'name': 'Personal and Demographic Information',
                'description': 'Basic personal information and demographics',
                'order': 1
            },
            {
                'name': 'Educational Background',
                'description': 'Information about educational history at CSU',
                'order': 2
            },
            {
                'name': 'Work History',
                'description': 'Employment details and work experience',
                'order': 3
            },
            {
                'name': 'Skills Relevance in Workplace',
                'description': 'Rate the relevance of different skills in your current work',
                'order': 4
            },
            {
                'name': 'Curriculum and Program Relevance',
                'description': 'Evaluate the usefulness of different courses and programs',
                'order': 5
            },
            {
                'name': 'Perception and Further Studies',
                'description': 'Views on graduate competitiveness and further education',
                'order': 6
            },
            {
                'name': 'Feedback and Recommendations',
                'description': 'Suggestions for program improvement',
                'order': 7
            }
        ]

        categories = {}
        for cat_data in categories_data:
            category = SurveyCategory.objects.create(
                name=cat_data['name'],
                description=cat_data['description'],
                order=cat_data['order'],
                is_active=True,
                created_by=super_admin
            )
            categories[cat_data['name']] = category
            self.stdout.write(f'Created category: {category.name}')

        # Section 1: Personal and Demographic Information
        personal_questions = [
            {
                'question_text': 'Full Name',
                'question_type': 'text',
                'is_required': True,
                'order': 1
            },
            {
                'question_text': 'Email Address',
                'question_type': 'email',
                'is_required': True,
                'order': 2
            },
            {
                'question_text': 'Mobile/Telephone Number',
                'question_type': 'text',
                'is_required': True,
                'order': 3
            },
            {
                'question_text': 'Sex',
                'question_type': 'radio',
                'options': ['Male', 'Female', 'Prefer not to say'],
                'is_required': True,
                'order': 4
            },
            {
                'question_text': 'Civil Status',
                'question_type': 'radio',
                'options': ['Single', 'Married', 'Separated', 'Widowed'],
                'is_required': True,
                'order': 5
            },
            {
                'question_text': 'Year of Birth',
                'question_type': 'number',
                'min_value': 1950,
                'max_value': 2010,
                'is_required': True,
                'order': 6
            },
            {
                'question_text': 'Present Address',
                'question_type': 'textarea',
                'is_required': True,
                'order': 7
            },
            {
                'question_text': 'Permanent Address',
                'question_type': 'textarea',
                'is_required': True,
                'order': 8
            },
            {
                'question_text': "Mother's Name",
                'question_type': 'text',
                'is_required': True,
                'order': 9
            },
            {
                'question_text': "Mother's Occupation",
                'question_type': 'text',
                'is_required': True,
                'order': 10
            },
            {
                'question_text': "Father's Name",
                'question_type': 'text',
                'is_required': True,
                'order': 11
            },
            {
                'question_text': "Father's Occupation",
                'question_type': 'text',
                'is_required': True,
                'order': 12
            }
        ]

        for q_data in personal_questions:
            question = SurveyQuestion.objects.create(
                category=categories['Personal and Demographic Information'],
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                options=q_data.get('options'),
                is_required=q_data['is_required'],
                min_value=q_data.get('min_value'),
                max_value=q_data.get('max_value'),
                order=q_data['order'],
                created_by=super_admin
            )

        # Section 2: Educational Background
        education_questions = [
            {
                'question_text': 'Year Graduated',
                'question_type': 'number',
                'min_value': 1990,
                'max_value': 2030,
                'is_required': True,
                'order': 1
            },
            {
                'question_text': 'Degree Taken at CSU',
                'question_type': 'text',
                'is_required': True,
                'order': 2
            }
        ]

        for q_data in education_questions:
            SurveyQuestion.objects.create(
                category=categories['Educational Background'],
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                is_required=q_data['is_required'],
                min_value=q_data.get('min_value'),
                max_value=q_data.get('max_value'),
                order=q_data['order'],
                created_by=super_admin
            )

        # Section 3: Work History (with conditional logic)
        work_questions = [
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
                'order': 2,
                'depends_on_question_text': 'Are you presently employed?',
                'depends_on_value': '["Yes"]'
            },
            {
                'question_text': 'Classification of Employment / Sector',
                'question_type': 'radio',
                'options': ['Government', 'Private', 'NGO', 'Freelance', 'Business Owner'],
                'is_required': True,
                'order': 3,
                'depends_on_question_text': 'Are you presently employed?',
                'depends_on_value': '["Yes"]'
            },
            {
                'question_text': 'Present Occupation',
                'question_type': 'text',
                'is_required': True,
                'order': 4,
                'depends_on_question_text': 'Are you presently employed?',
                'depends_on_value': '["Yes"]'
            },
            {
                'question_text': 'Employing Agency Name & Location',
                'question_type': 'text',
                'is_required': True,
                'order': 5,
                'depends_on_question_text': 'Are you presently employed?',
                'depends_on_value': '["Yes"]'
            },
            {
                'question_text': 'How did you get your current job?',
                'question_type': 'text',
                'is_required': True,
                'order': 6,
                'depends_on_question_text': 'Are you presently employed?',
                'depends_on_value': '["Yes"]'
            },
            {
                'question_text': 'Monthly Income',
                'question_type': 'radio',
                'options': ['Less than ₱15,000', '₱15,000 – ₱29,999', '₱30,000 – ₱49,999', '₱50,000 and above', 'Prefer not to say'],
                'is_required': True,
                'order': 7,
                'depends_on_question_text': 'Are you presently employed?',
                'depends_on_value': '["Yes"]'
            },
            {
                'question_text': 'Are you the breadwinner?',
                'question_type': 'yes_no',
                'is_required': True,
                'order': 8,
                'depends_on_question_text': 'Are you presently employed?',
                'depends_on_value': '["Yes"]'
            },
            {
                'question_text': 'Length of Service (Years / Months)',
                'question_type': 'text',
                'is_required': True,
                'order': 9,
                'depends_on_question_text': 'Are you presently employed?',
                'depends_on_value': '["Yes"]'
            },
            {
                'question_text': 'Was college education relevant to this job?',
                'question_type': 'radio',
                'options': ['Yes', 'No', 'Somewhat'],
                'is_required': True,
                'order': 10,
                'depends_on_question_text': 'Are you presently employed?',
                'depends_on_value': '["Yes"]'
            },
            {
                'question_text': 'Is your current job your first job?',
                'question_type': 'yes_no',
                'is_required': True,
                'order': 11,
                'depends_on_question_text': 'Are you presently employed?',
                'depends_on_value': '["Yes"]'
            },
            {
                'question_text': 'First Job Title',
                'question_type': 'text',
                'is_required': True,
                'order': 12,
                'depends_on_question_text': 'Is your current job your first job?',
                'depends_on_value': '["No"]'
            },
            {
                'question_text': 'First Employer',
                'question_type': 'text',
                'is_required': True,
                'order': 13,
                'depends_on_question_text': 'Is your current job your first job?',
                'depends_on_value': '["No"]'
            },
            {
                'question_text': 'Employment Status in First Job',
                'question_type': 'radio',
                'options': ['Employed Locally', 'Employed Internationally', 'Self-employed', 'Unemployed', 'Retired'],
                'is_required': True,
                'order': 14,
                'depends_on_question_text': 'Is your current job your first job?',
                'depends_on_value': '["No"]'
            },
            {
                'question_text': 'Sector Classification (First Job)',
                'question_type': 'radio',
                'options': ['Government', 'Private', 'NGO', 'Freelance', 'Business Owner'],
                'is_required': True,
                'order': 15,
                'depends_on_question_text': 'Is your current job your first job?',
                'depends_on_value': '["No"]'
            },
            {
                'question_text': 'How did you get your first job?',
                'question_type': 'text',
                'is_required': True,
                'order': 16,
                'depends_on_question_text': 'Is your current job your first job?',
                'depends_on_value': '["No"]'
            },
            {
                'question_text': 'Monthly Income in First Job',
                'question_type': 'radio',
                'options': ['Less than ₱15,000', '₱15,000 – ₱29,999', '₱30,000 – ₱49,999', '₱50,000 and above', 'Prefer not to say'],
                'is_required': True,
                'order': 17,
                'depends_on_question_text': 'Is your current job your first job?',
                'depends_on_value': '["No"]'
            },
            {
                'question_text': 'Length of Service in First Job (Years / Months)',
                'question_type': 'text',
                'is_required': True,
                'order': 18,
                'depends_on_question_text': 'Is your current job your first job?',
                'depends_on_value': '["No"]'
            },
            {
                'question_text': 'Was college education relevant to first job?',
                'question_type': 'radio',
                'options': ['Yes', 'No', 'Somewhat'],
                'is_required': True,
                'order': 19,
                'depends_on_question_text': 'Is your current job your first job?',
                'depends_on_value': '["No"]'
            }
        ]

        work_questions_map = {}
        for q_data in work_questions:
            question = SurveyQuestion.objects.create(
                category=categories['Work History'],
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                options=q_data.get('options'),
                is_required=q_data['is_required'],
                order=q_data['order'],
                created_by=super_admin
            )
            work_questions_map[q_data['question_text']] = question

        # Now set up conditional dependencies for work questions
        for q_data in work_questions:
            if 'depends_on_question_text' in q_data:
                question = work_questions_map[q_data['question_text']]
                depends_on_question = work_questions_map[q_data['depends_on_question_text']]
                question.depends_on_question = depends_on_question
                question.depends_on_value = q_data['depends_on_value']
                question.save()

        # Section 4: Skills Relevance
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

        for i, skill in enumerate(skills_questions, 1):
            SurveyQuestion.objects.create(
                category=categories['Skills Relevance in Workplace'],
                question_text=f'Rate the relevance of {skill} in your work',
                question_type='rating',
                is_required=True,
                min_value=1,
                max_value=5,
                help_text='1 = Not Useful, 5 = Very Useful',
                order=i,
                created_by=super_admin
            )

        # Section 5: Curriculum and Program Relevance
        curriculum_questions = [
            'General Education / Minor Courses',
            'Core / Major Courses',
            'Special Professional Courses',
            'Electives',
            'Internship / OJT',
            'Co-Curricular Activities (e.g., seminars, field trips)',
            'Extra-Curricular Activities (e.g., intramurals, exit conference)'
        ]

        for i, curriculum_item in enumerate(curriculum_questions, 1):
            category_name = 'Curriculum and Program Relevance'
            if i > 5:
                question_text = f'How useful are {curriculum_item} in your professional work?'
            else:
                question_text = f'How useful are {curriculum_item} in your professional work?'
            
            SurveyQuestion.objects.create(
                category=categories[category_name],
                question_text=question_text,
                question_type='rating',
                is_required=True,
                min_value=1,
                max_value=5,
                help_text='1 = Not Useful, 5 = Very Useful',
                order=i,
                created_by=super_admin
            )

        # Section 6: Perception and Further Studies
        perception_questions = [
            {
                'question_text': 'Rate the competitiveness of graduates (1-5)',
                'question_type': 'rating',
                'min_value': 1,
                'max_value': 5,
                'is_required': True,
                'order': 1
            },
            {
                'question_text': 'Have you pursued further studies?',
                'question_type': 'yes_no',
                'is_required': True,
                'order': 2
            },
            {
                'question_text': 'Mode of Study',
                'question_type': 'radio',
                'options': ['Full-time', 'Part-time', 'Online', 'Others'],
                'is_required': True,
                'order': 3,
                'depends_on_question_text': 'Have you pursued further studies?',
                'depends_on_value': '[true]'
            },
            {
                'question_text': 'Level of Study',
                'question_type': 'radio',
                'options': ["Master's", 'Doctoral', 'Certificate'],
                'is_required': True,
                'order': 4,
                'depends_on_question_text': 'Have you pursued further studies?',
                'depends_on_value': '[true]'
            },
            {
                'question_text': 'Field of Study',
                'question_type': 'text',
                'is_required': True,
                'order': 5,
                'depends_on_question_text': 'Have you pursued further studies?',
                'depends_on_value': '[true]'
            },
            {
                'question_text': 'Specialization',
                'question_type': 'text',
                'is_required': True,
                'order': 6,
                'depends_on_question_text': 'Have you pursued further studies?',
                'depends_on_value': '[true]'
            },
            {
                'question_text': 'Is it related to your undergrad?',
                'question_type': 'yes_no',
                'is_required': True,
                'order': 7,
                'depends_on_question_text': 'Have you pursued further studies?',
                'depends_on_value': '[true]'
            },
            {
                'question_text': 'Reasons for further study',
                'question_type': 'checkbox',
                'options': ['Career growth', 'Interest', 'Job requirement', 'Promotion', 'Personal development', 'Others'],
                'is_required': True,
                'order': 8,
                'depends_on_question_text': 'Have you pursued further studies?',
                'depends_on_value': '[true]'
            }
        ]

        perception_questions_map = {}
        for q_data in perception_questions:
            question = SurveyQuestion.objects.create(
                category=categories['Perception and Further Studies'],
                question_text=q_data['question_text'],
                question_type=q_data['question_type'],
                options=q_data.get('options'),
                is_required=q_data['is_required'],
                min_value=q_data.get('min_value'),
                max_value=q_data.get('max_value'),
                order=q_data['order'],
                created_by=super_admin
            )
            perception_questions_map[q_data['question_text']] = question

        # Set up conditional dependencies for perception questions
        for q_data in perception_questions:
            if 'depends_on_question_text' in q_data:
                question = perception_questions_map[q_data['question_text']]
                depends_on_question = perception_questions_map[q_data['depends_on_question_text']]
                question.depends_on_question = depends_on_question
                question.depends_on_value = q_data['depends_on_value']
                question.save()

        # Section 7: Feedback and Recommendations
        SurveyQuestion.objects.create(
            category=categories['Feedback and Recommendations'],
            question_text='What are your recommendations to improve the program you had in college?',
            question_type='textarea',
            is_required=True,
            order=1,
            created_by=super_admin
        )

        self.stdout.write(self.style.SUCCESS('Successfully created Alumni Tracer Survey'))
        self.stdout.write(f'Created {SurveyCategory.objects.count()} categories')
        self.stdout.write(f'Created {SurveyQuestion.objects.count()} questions')
