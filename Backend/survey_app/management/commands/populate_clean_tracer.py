import re
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from survey_app.models import SurveyCategory, SurveyQuestion

User = get_user_model()

class Command(BaseCommand):
    help = 'Create clean Alumni Tracer Survey with proper question types and conditional logic'

    def add_arguments(self, parser):
        parser.add_argument(
            '--admin-email',
            type=str,
            default='admin@alumni.system',
            help='Email of the admin user who will be set as creator'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be created without actually creating it'
        )

    def handle(self, *args, **options):
        admin_email = options['admin_email']
        dry_run = options['dry_run']

        # Get admin user
        admin_user = User.objects.filter(email=admin_email).first()
        if not admin_user:
            admin_user = User.objects.filter(user_type__in=[1, 2]).first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found. Please create admin accounts first.'))
            return

        # Get the clean survey structure
        survey_data = self.get_clean_survey_structure()

        if dry_run:
            self.show_dry_run_preview(survey_data)
            return
        
        # Clear existing survey data
        SurveyQuestion.objects.all().delete()
        SurveyCategory.objects.all().delete()
        
        # Create the survey
        self.create_survey_structure(survey_data, admin_user)

    def get_clean_survey_structure(self):
        """Define the clean, well-structured Alumni Tracer Survey based on official tracer.txt"""
        return {
            "Present Employment": {
                "description": "Current employment information and job details",
                "order": 1,
                "questions": [
                    {
                        "question": "Are you presently employed?",
                        "type": "select",
                        "options": ["Yes", "No", "Never been employed"],
                        "conditional": None,
                        "order": 1
                    },
                    {
                        "question": "Present Employment Status",
                        "type": "select",
                        "options": ["Employed Locally", "Employed Internationally", "Self-employed", "Unemployed", "Retired"],
                        "conditional": {"depends_on": "Are you presently employed?", "show_when": "Yes"},
                        "order": 2
                    },
                    {
                        "question": "Classification of Employment/Sector",
                        "type": "select", 
                        "options": ["Government", "Private", "NGO", "Freelance", "Business Owner"],
                        "conditional": {"depends_on": "Are you presently employed?", "show_when": "Yes"},
                        "order": 3
                    },
                    {
                        "question": "Present Occupation",
                        "type": "text",
                        "options": [],
                        "conditional": {"depends_on": "Are you presently employed?", "show_when": "Yes"},
                        "order": 4
                    },
                    {
                        "question": "Employing Agency Name & Location",
                        "type": "text",
                        "options": [],
                        "conditional": {"depends_on": "Are you presently employed?", "show_when": "Yes"},
                        "order": 5
                    },
                    {
                        "question": "How did you get your current job?",
                        "type": "select",
                        "options": ["Walk-in", "Online Job Portal", "Referral", "Job Fair", "Internship Connection", "Social Media", "Others"],
                        "conditional": {"depends_on": "Are you presently employed?", "show_when": "Yes"},
                        "order": 6
                    },
                    {
                        "question": "Monthly Income Range",
                        "type": "select",
                        "options": ["<₱15,000", "₱15,000–₱29,999", "₱30,000–₱49,999", "₱50,000+", "Prefer not to say"],
                        "conditional": {"depends_on": "Are you presently employed?", "show_when": "Yes"},
                        "order": 7
                    },
                    {
                        "question": "Are you the breadwinner?",
                        "type": "yes_no",
                        "options": [],
                        "conditional": {"depends_on": "Are you presently employed?", "show_when": "Yes"},
                        "order": 8
                    },
                    {
                        "question": "Length of Service (Years/Months)",
                        "type": "text",
                        "options": [],
                        "conditional": {"depends_on": "Are you presently employed?", "show_when": "Yes"},
                        "order": 9
                    },
                    {
                        "question": "Was college education relevant to your job?",
                        "type": "select",
                        "options": ["Yes", "No", "Somewhat"],
                        "conditional": {"depends_on": "Are you presently employed?", "show_when": "Yes"},
                        "order": 10
                    }
                ]
            },
            "First Job": {
                "description": "Information about your first job (if different from current)",
                "order": 2,
                "questions": [
                    {
                        "question": "Is your current job your first job?",
                        "type": "yes_no",
                        "options": [],
                        "conditional": None,
                        "order": 1
                    },
                    {
                        "question": "First Job Title",
                        "type": "text",
                        "options": [],
                        "conditional": {"depends_on": "Is your current job your first job?", "show_when": "No"},
                        "order": 2
                    },
                    {
                        "question": "First Employer",
                        "type": "text",
                        "options": [],
                        "conditional": {"depends_on": "Is your current job your first job?", "show_when": "No"},
                        "order": 3
                    },
                    {
                        "question": "Employment Status in First Job",
                        "type": "select",
                        "options": ["Full-Time", "Part-Time", "Contractual", "Probationary", "Freelance"],
                        "conditional": {"depends_on": "Is your current job your first job?", "show_when": "No"},
                        "order": 4
                    },
                    {
                        "question": "Sector Classification (First Job)",
                        "type": "select",
                        "options": ["Government", "Private", "NGO", "Freelance", "Business Owner"],
                        "conditional": {"depends_on": "Is your current job your first job?", "show_when": "No"},
                        "order": 5
                    },
                    {
                        "question": "How did you get your first job?",
                        "type": "select",
                        "options": ["Walk-in", "Online Job Portal", "Referral", "Job Fair", "Internship", "Social Media", "Others"],
                        "conditional": {"depends_on": "Is your current job your first job?", "show_when": "No"},
                        "order": 6
                    },
                    {
                        "question": "Monthly Income in First Job",
                        "type": "select",
                        "options": ["<₱15,000", "₱15,000–₱29,999", "₱30,000–₱49,999", "₱50,000+", "Prefer not to say"],
                        "conditional": {"depends_on": "Is your current job your first job?", "show_when": "No"},
                        "order": 7
                    },
                    {
                        "question": "Length of Service (Years/Months)",
                        "type": "text",
                        "options": [],
                        "conditional": {"depends_on": "Is your current job your first job?", "show_when": "No"},
                        "order": 8
                    },
                    {
                        "question": "Was college education relevant to your first job?",
                        "type": "select",
                        "options": ["Yes", "No", "Somewhat"],
                        "conditional": {"depends_on": "Is your current job your first job?", "show_when": "No"},
                        "order": 9
                    }
                ]
            },
            "Skills Relevance in the Workplace": {
                "description": "Rate the relevance of each skill in your work (1–Not Useful | 5–Very Useful)",
                "order": 3,
                "questions": [
                    {
                        "question": "Critical Thinking",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 1
                    },
                    {
                        "question": "Communication", 
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 2
                    },
                    {
                        "question": "Innovation",
                        "type": "rating", 
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 3
                    },
                    {
                        "question": "Collaboration",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 4
                    },
                    {
                        "question": "Leadership",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 5
                    },
                    {
                        "question": "Productivity and Accountability",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 6
                    },
                    {
                        "question": "Entrepreneurship",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 7
                    },
                    {
                        "question": "Global Citizenship",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 8
                    },
                    {
                        "question": "Adaptability",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 9
                    },
                    {
                        "question": "Accessing, Analyzing, and Synthesizing Information",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 10
                    }
                ]
            },
            "Curriculum and Program Relevance": {
                "description": "Rate the usefulness of each course and program (1–Not Useful | 5–Very Useful)",
                "order": 4,
                "questions": [
                    {
                        "question": "General Education / Minor Courses",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 1
                    },
                    {
                        "question": "Core / Major Courses",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 2
                    },
                    {
                        "question": "Special Professional Courses",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 3
                    },
                    {
                        "question": "Electives",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 4
                    },
                    {
                        "question": "Internship / OJT",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 5
                    },
                    {
                        "question": "Co-Curricular (e.g., seminars, field trips)",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 6
                    },
                    {
                        "question": "Extra-Curricular (e.g., intramurals, exit conference)",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 7
                    }
                ]
            },
            "Perception and Further Studies": {
                "description": "Information about your further education and competitiveness perception",
                "order": 5,
                "questions": [
                    {
                        "question": "Competitiveness of graduates (1–Not Competitive | 5–Very Competitive)",
                        "type": "rating",
                        "min_value": 1,
                        "max_value": 5,
                        "conditional": None,
                        "order": 1
                    },
                    {
                        "question": "Have you pursued further studies?",
                        "type": "yes_no",
                        "options": [],
                        "conditional": None,
                        "order": 2
                    },
                    {
                        "question": "Mode of Study",
                        "type": "select",
                        "options": ["Full-Time", "Part-Time", "Online", "Others"],
                        "conditional": {"depends_on": "Have you pursued further studies?", "show_when": "Yes"},
                        "order": 3
                    },
                    {
                        "question": "Level of Study",
                        "type": "select",
                        "options": ["Master's", "Doctoral", "Certificate", "Others"],
                        "conditional": {"depends_on": "Have you pursued further studies?", "show_when": "Yes"},
                        "order": 4
                    },
                    {
                        "question": "Field of Study",
                        "type": "text",
                        "options": [],
                        "conditional": {"depends_on": "Have you pursued further studies?", "show_when": "Yes"},
                        "order": 5
                    },
                    {
                        "question": "Specialization",
                        "type": "text",
                        "options": [],
                        "conditional": {"depends_on": "Have you pursued further studies?", "show_when": "Yes"},
                        "order": 6
                    },
                    {
                        "question": "Is it related to your undergraduate degree?",
                        "type": "yes_no",
                        "options": [],
                        "conditional": {"depends_on": "Have you pursued further studies?", "show_when": "Yes"},
                        "order": 7
                    },
                    {
                        "question": "Reasons for pursuing further studies (check all that apply)",
                        "type": "checkbox",
                        "options": ["Career Growth", "Personal Interest", "Job Requirement", "Promotion Opportunity", "Personal Development", "Others"],
                        "conditional": {"depends_on": "Have you pursued further studies?", "show_when": "Yes"},
                        "order": 8
                    }
                ]
            },
            "Feedback and Recommendations": {
                "description": "Your feedback to improve the program",
                "order": 6,
                "questions": [
                    {
                        "question": "What are your recommendations to improve the program you had in college?",
                        "type": "textarea",
                        "options": [],
                        "conditional": None,
                        "order": 1
                    }
                ]
            }
        }

    def show_dry_run_preview(self, survey_data):
        """Show what would be created"""
        self.stdout.write(self.style.SUCCESS('=== DRY RUN PREVIEW ===\n'))
        
        total_questions = 0
        conditional_questions = 0
        
        for category_name, category_data in survey_data.items():
            questions = category_data['questions']
            conditional_count = sum(1 for q in questions if q['conditional'])
            total_questions += len(questions)
            conditional_questions += conditional_count
            
            self.stdout.write(f"📁 {category_name} (Order: {category_data['order']})")
            self.stdout.write(f"   Description: {category_data['description']}")
            self.stdout.write(f"   Questions: {len(questions)} ({conditional_count} conditional)")
            
            for question in questions:
                status = "🔗" if question['conditional'] else "❓"
                q_type = question['type'].upper()
                options_count = len(question['options'])
                self.stdout.write(f"   {status} [{q_type}] {question['question']}")
                if options_count > 0:
                    self.stdout.write(f"      Options: {options_count} ({', '.join(question['options'][:3])}{'...' if options_count > 3 else ''})")
                if question['conditional']:
                    cond = question['conditional']
                    self.stdout.write(f"      Conditional: Show when '{cond['depends_on']}' = '{cond['show_when']}'")
            
            self.stdout.write('')
        
        self.stdout.write(f"📊 Total: {len(survey_data)} categories, {total_questions} questions, {conditional_questions} conditional")

    def create_survey_structure(self, survey_data, admin_user):
        """Create the survey in the database"""
        self.stdout.write(self.style.SUCCESS('Creating Alumni Tracer Survey...'))
        
        categories_created = 0
        questions_created = 0
        conditionals_created = 0
        
        # Track questions for conditional logic
        question_map = {}
        
        for category_name, category_data in survey_data.items():
            # Create category
            category = SurveyCategory.objects.create(
                name=category_name,
                description=category_data['description'],
                order=category_data['order'],
                is_active=True,
                created_by=admin_user
            )
            categories_created += 1
            
            # Create questions
            for question_data in category_data['questions']:
                # Handle rating questions properly
                min_value = question_data.get('min_value', None)
                max_value = question_data.get('max_value', None)
                options = question_data.get('options', [])
                
                if question_data['type'] == 'rating':
                    # For rating questions, don't use options array
                    options = None
                
                question = SurveyQuestion.objects.create(
                    category=category,
                    question_text=question_data['question'],
                    question_type=question_data['type'],
                    options=options,
                    min_value=min_value,
                    max_value=max_value,
                    order=question_data['order'],
                    is_required=True,
                    is_active=True,
                    created_by=admin_user
                )
                questions_created += 1
                
                # Store for conditional logic
                question_map[question_data['question']] = question
        
        # Second pass: Set up conditional logic
        for category_name, category_data in survey_data.items():
            for question_data in category_data['questions']:
                if question_data['conditional']:
                    current_question = question_map[question_data['question']]
                    depends_on_text = question_data['conditional']['depends_on']
                    show_when = question_data['conditional']['show_when']
                    
                    if depends_on_text in question_map:
                        depends_on_question = question_map[depends_on_text]
                        current_question.depends_on_question = depends_on_question
                        current_question.depends_on_value = show_when
                        current_question.save()
                        conditionals_created += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Alumni Tracer Survey Created Successfully!\n'
                f'📁 Categories: {categories_created}\n'
                f'❓ Questions: {questions_created}\n'
                f'🔗 Conditional Logic: {conditionals_created}\n'
                f'\n🌐 Access via Admin/SuperAdmin Dashboard -> Survey Management\n'
                f'📋 Survey is ready for alumni to complete!'
            )
        )