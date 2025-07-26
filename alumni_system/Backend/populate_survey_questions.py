#!/usr/bin/env python
"""
Script to populate initial survey questions for Alumni Tracer
Run this script with: python populate_survey_questions.py
"""

import os
import django
import sys

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

from auth_app.models import SurveyCategory, SurveyQuestion

def create_survey_questions():
    """Create the Alumni Tracer survey questions"""
    
    # Clear existing data
    SurveyQuestion.objects.all().delete()
    SurveyCategory.objects.all().delete()
    
    # Define categories and questions
    survey_data = [
        {
            'category': 'Basic Information',
            'order': 1,
            'questions': [
                {'text': 'Present Address', 'type': 'textarea', 'required': True, 'order': 1},
                {'text': 'Permanent Address', 'type': 'textarea', 'required': True, 'order': 2},
                {'text': 'Mobile/Telephone Number', 'type': 'text', 'required': True, 'order': 3},
                {'text': 'Sex', 'type': 'radio', 'required': True, 'order': 4, 'options': ['Male', 'Female']},
                {'text': 'Civil Status', 'type': 'select', 'required': True, 'order': 5, 'options': ['Single', 'Married', 'Divorced', 'Widowed']},
                {'text': 'Year of Birth', 'type': 'number', 'required': True, 'order': 6},
            ]
        },
        {
            'category': 'Parental Background',
            'order': 2,
            'questions': [
                {'text': "Mother's Occupation", 'type': 'text', 'required': True, 'order': 1},
                {'text': "Father's Occupation", 'type': 'text', 'required': True, 'order': 2},
            ]
        },
        {
            'category': 'Educational Background',
            'order': 3,
            'questions': [
                {'text': 'Year Graduated', 'type': 'number', 'required': True, 'order': 1},
                {'text': 'Degree Taken at CSU', 'type': 'text', 'required': True, 'order': 2},
            ]
        },
        {
            'category': 'Employment Information',
            'order': 4,
            'questions': [
                {'text': 'Are you presently employed?', 'type': 'yes_no', 'required': True, 'order': 1},
                {'text': 'Present Employment Status', 'type': 'select', 'required': True, 'order': 2, 'options': ['Employed Locally', 'Employed Internationally', 'Self-Employed', 'Unemployed']},
                {'text': 'Classification of Employment / Sector', 'type': 'select', 'required': True, 'order': 3, 'options': ['Government', 'Private', 'NGO', 'Self-Employed', 'Other']},
                {'text': 'Present Occupation', 'type': 'text', 'required': True, 'order': 4},
                {'text': 'Name of Employing Agency and Location of Employment (Local/Abroad)', 'type': 'textarea', 'required': True, 'order': 5},
                {'text': 'How did you get your present job?', 'type': 'select', 'required': True, 'order': 6, 'options': ['Through referral', 'Job posting/advertisement', 'Direct application', 'Networking', 'Family business', 'Other']},
                {'text': 'What is your monthly income in your present job?', 'type': 'select', 'required': True, 'order': 7, 'options': ['Below 10,000', '10,000-20,000', '20,001-30,000', '30,001-50,000', '50,001-100,000', 'Above 100,000']},
                {'text': 'Are you the breadwinner in your household?', 'type': 'yes_no', 'required': True, 'order': 8},
                {'text': 'Length of service in present job (Years)', 'type': 'number', 'required': True, 'order': 9},
                {'text': 'Length of service in present job (Months)', 'type': 'number', 'required': True, 'order': 10},
                {'text': 'Was college education relevant to your present job?', 'type': 'rating', 'required': True, 'order': 11, 'options': ['1', '2', '3', '4', '5']},
            ]
        },
        {
            'category': 'First Job Information',
            'order': 5,
            'questions': [
                {'text': 'Is your present job your first job since college?', 'type': 'yes_no', 'required': True, 'order': 1},
                {'text': 'What was your first job?', 'type': 'text', 'required': False, 'order': 2},
                {'text': 'Name of Employing Agency (First Job)', 'type': 'text', 'required': False, 'order': 3},
                {'text': 'Employment Status in your First Job', 'type': 'select', 'required': False, 'order': 4, 'options': ['Regular/Permanent', 'Contractual', 'Casual', 'Temporary', 'Self-Employed']},
                {'text': 'Classification of Employment in your First Job', 'type': 'select', 'required': False, 'order': 5, 'options': ['Government', 'Private', 'NGO', 'Self-Employed', 'Other']},
                {'text': 'How did you get your first job?', 'type': 'select', 'required': False, 'order': 6, 'options': ['Through referral', 'Job posting/advertisement', 'Direct application', 'Networking', 'Family business', 'Other']},
                {'text': 'What was your monthly income in your first job?', 'type': 'select', 'required': False, 'order': 7, 'options': ['Below 10,000', '10,000-20,000', '20,001-30,000', '30,001-50,000', '50,001-100,000', 'Above 100,000']},
                {'text': 'Length of service in first job (Years)', 'type': 'number', 'required': False, 'order': 8},
                {'text': 'Length of service in first job (Months)', 'type': 'number', 'required': False, 'order': 9},
                {'text': 'Was college education relevant to your first job?', 'type': 'rating', 'required': False, 'order': 10, 'options': ['1', '2', '3', '4', '5']},
            ]
        },
        {
            'category': 'Workplace Skills',
            'order': 6,
            'questions': [
                {'text': 'Rate the relevance of Critical Thinking in your professional work', 'type': 'rating', 'required': True, 'order': 1, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'Rate the relevance of Communication in your professional work', 'type': 'rating', 'required': True, 'order': 2, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'Rate the relevance of Innovation in your professional work', 'type': 'rating', 'required': True, 'order': 3, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'Rate the relevance of Collaboration in your professional work', 'type': 'rating', 'required': True, 'order': 4, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'Rate the relevance of Leadership in your professional work', 'type': 'rating', 'required': True, 'order': 5, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'Rate the relevance of Productivity and Accountability in your professional work', 'type': 'rating', 'required': True, 'order': 6, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'Rate the relevance of Entrepreneurship in your professional work', 'type': 'rating', 'required': True, 'order': 7, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'Rate the relevance of Global Citizenship in your professional work', 'type': 'rating', 'required': True, 'order': 8, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'Rate the relevance of Adaptability in your professional work', 'type': 'rating', 'required': True, 'order': 9, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'Rate the relevance of Accessing, Analyzing, and Synthesizing Information in your professional work', 'type': 'rating', 'required': True, 'order': 10, 'options': ['1', '2', '3', '4', '5']},
            ]
        },
        {
            'category': 'Curriculum Relevance',
            'order': 7,
            'questions': [
                {'text': 'How useful are General Education Courses / Minor Courses in your professional work?', 'type': 'rating', 'required': True, 'order': 1, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'How useful are Core / Major Courses in your professional work?', 'type': 'rating', 'required': True, 'order': 2, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'How useful are Special Professional Courses in your professional work?', 'type': 'rating', 'required': True, 'order': 3, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'How useful are Elective Courses in your professional work?', 'type': 'rating', 'required': True, 'order': 4, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'How useful is Internship / On-the-Job Training (OJT) in your professional work?', 'type': 'rating', 'required': True, 'order': 5, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'How useful are Co-Curricular Activities (e.g. field trips, seminars) in your professional work?', 'type': 'rating', 'required': True, 'order': 6, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'How useful are Extra-Curricular Activities (e.g. intramurals, exit conference) in your professional work?', 'type': 'rating', 'required': True, 'order': 7, 'options': ['1', '2', '3', '4', '5']},
            ]
        },
        {
            'category': 'Perception and Further Studies',
            'order': 8,
            'questions': [
                {'text': 'How competitive are the graduates of your course in the job market?', 'type': 'rating', 'required': True, 'order': 1, 'options': ['1', '2', '3', '4', '5']},
                {'text': 'Have you done any further studies after completing your baccalaureate degree?', 'type': 'yes_no', 'required': True, 'order': 2},
                {'text': 'Mode of Study', 'type': 'select', 'required': False, 'order': 3, 'options': ['Full-time', 'Part-time', 'Online', 'Distance Learning']},
                {'text': 'Level of Study', 'type': 'select', 'required': False, 'order': 4, 'options': ['Certificate', 'Diploma', 'Masters', 'PhD/Doctorate', 'Professional']},
                {'text': 'Field of Study', 'type': 'text', 'required': False, 'order': 5},
                {'text': 'Specialization', 'type': 'text', 'required': False, 'order': 6},
                {'text': 'Is the area of study similar or related to your previous areas of study?', 'type': 'yes_no', 'required': False, 'order': 7},
                {'text': 'What are your reasons for further studies?', 'type': 'checkbox', 'required': False, 'order': 8, 'options': ['Career advancement', 'Personal interest', 'Employer requirement', 'Salary increase', 'Job requirement', 'Other']},
            ]
        },
        {
            'category': 'Feedback',
            'order': 9,
            'questions': [
                {'text': 'What are your recommendations to improve the program you had in college?', 'type': 'textarea', 'required': True, 'order': 1},
            ]
        }
    ]
    
    # Create categories and questions
    for category_data in survey_data:
        category = SurveyCategory.objects.create(
            name=category_data['category'],
            order=category_data['order']
        )
        
        for question_data in category_data['questions']:
            SurveyQuestion.objects.create(
                category=category,
                question_text=question_data['text'],
                question_type=question_data['type'],
                options=question_data.get('options', []),
                is_required=question_data['required'],
                order=question_data['order']
            )
    
    print("✅ Alumni Tracer Survey questions created successfully!")
    print(f"Created {SurveyCategory.objects.count()} categories")
    print(f"Created {SurveyQuestion.objects.count()} questions")

if __name__ == '__main__':
    create_survey_questions()
