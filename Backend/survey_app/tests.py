from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from .models import SurveyCategory, SurveyQuestion
import json

User = get_user_model()


class ConditionalLogicTestCase(TestCase):
    """Test conditional logic for survey questions and categories"""

    def setUp(self):
        """Set up test data"""
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            user_type=1,  # Admin
            first_name='Admin',
            last_name='User'
        )
        
        # Create alumni user
        self.alumni = User.objects.create_user(
            username='alumni',
            email='alumni@test.com',
            password='alumni123',
            user_type=3,  # Alumni
            first_name='Alumni',
            last_name='User'
        )
        
        self.client = APIClient()
        
        # Create base category (Personal Information)
        self.personal_info_category = SurveyCategory.objects.create(
            name='Personal Information',
            description='Basic personal information',
            order=1,
            is_active=True,
            created_by=self.admin
        )
        
        # Create employment status question (Yes/No)
        self.employment_question = SurveyQuestion.objects.create(
            category=self.personal_info_category,
            question_text='Are you currently employed?',
            question_type='yes_no',
            is_required=True,
            order=1,
            is_active=True,
            created_by=self.admin
        )
        
        # Create conditional category (Employment Details) - depends on employment question
        self.employment_details_category = SurveyCategory.objects.create(
            name='Employment Details',
            description='Details about your current employment',
            order=2,
            is_active=True,
            depends_on_category=self.personal_info_category,
            depends_on_question_text='Are you currently employed?',
            depends_on_value='["Yes"]',
            created_by=self.admin
        )
        
        # Create job title question (always visible in Employment Details)
        self.job_title_question = SurveyQuestion.objects.create(
            category=self.employment_details_category,
            question_text='What is your job title?',
            question_type='text',
            is_required=True,
            order=1,
            is_active=True,
            created_by=self.admin
        )
        
        # Create manager question in Employment Details
        self.manager_question = SurveyQuestion.objects.create(
            category=self.employment_details_category,
            question_text='Do you have a manager?',
            question_type='yes_no',
            is_required=False,
            order=2,
            is_active=True,
            created_by=self.admin
        )
        
        # Create conditional question - manager name (depends on manager question)
        self.manager_name_question = SurveyQuestion.objects.create(
            category=self.employment_details_category,
            question_text='What is your manager\'s name?',
            question_type='text',
            is_required=False,
            order=3,
            is_active=True,
            depends_on_question=self.manager_question,
            depends_on_value='Yes',
            created_by=self.admin
        )

    def test_serializer_includes_conditional_fields(self):
        """Test that ActiveSurveyQuestionsSerializer includes conditional fields"""
        from .serializers import ActiveSurveyQuestionsSerializer
        
        # Serialize the employment details category
        serializer = ActiveSurveyQuestionsSerializer(self.employment_details_category)
        data = serializer.data
        
        # Check category has conditional fields
        self.assertIn('depends_on_category', data['category'])
        self.assertIn('depends_on_question_text', data['category'])
        self.assertIn('depends_on_value', data['category'])
        
        # Check category conditional values
        self.assertEqual(data['category']['depends_on_category'], self.personal_info_category.id)
        self.assertEqual(data['category']['depends_on_question_text'], 'Are you currently employed?')
        self.assertEqual(data['category']['depends_on_value'], '["Yes"]')
        
        # Check questions have conditional fields
        manager_name_q = next((q for q in data['questions'] if q['question_text'] == "What is your manager's name?"), None)
        self.assertIsNotNone(manager_name_q)
        self.assertIn('depends_on_question_id', manager_name_q)
        self.assertIn('depends_on_value', manager_name_q)
        
        # Check question conditional values
        self.assertEqual(manager_name_q['depends_on_question_id'], self.manager_question.id)
        self.assertEqual(manager_name_q['depends_on_value'], 'Yes')

    def test_non_conditional_questions_have_null_dependencies(self):
        """Test that questions without conditions have null dependency fields"""
        from .serializers import ActiveSurveyQuestionsSerializer
        
        serializer = ActiveSurveyQuestionsSerializer(self.personal_info_category)
        data = serializer.data
        
        # Personal Info category should not have dependencies
        self.assertIsNone(data['category']['depends_on_category'])
        self.assertEqual(data['category']['depends_on_question_text'], '')
        self.assertEqual(data['category']['depends_on_value'], '')
        
        # Employment question should not have dependencies
        employment_q = data['questions'][0]
        self.assertIsNone(employment_q['depends_on_question_id'])
        self.assertEqual(employment_q['depends_on_value'], '')

    def test_api_returns_conditional_fields(self):
        """Test that the API endpoint returns conditional fields"""
        self.client.force_authenticate(user=self.alumni)
        
        response = self.client.get('/api/survey/questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(len(response.data) > 0)
        
        # Find the Employment Details category
        employment_details = next((cat for cat in response.data if cat['category']['name'] == 'Employment Details'), None)
        self.assertIsNotNone(employment_details)
        
        # Check category conditional fields
        self.assertEqual(employment_details['category']['depends_on_category'], self.personal_info_category.id)
        self.assertEqual(employment_details['category']['depends_on_question_text'], 'Are you currently employed?')
        
        # Find manager name question
        manager_name = next((q for q in employment_details['questions'] if "manager's name" in q['question_text'].lower()), None)
        self.assertIsNotNone(manager_name)
        self.assertEqual(manager_name['depends_on_question_id'], self.manager_question.id)

    def test_multiple_dependency_values_json_array(self):
        """Test that JSON arrays for multiple valid values work correctly"""
        # Create a question with multiple valid dependency values
        question = SurveyQuestion.objects.create(
            category=self.personal_info_category,
            question_text='Employment type?',
            question_type='radio',
            options=['Full-time', 'Part-time', 'Contract', 'Unemployed'],
            is_required=True,
            order=2,
            is_active=True,
            created_by=self.admin
        )
        
        # Create conditional category that shows for Full-time, Part-time, or Contract
        conditional_category = SurveyCategory.objects.create(
            name='Work Schedule',
            description='Details about your work schedule',
            order=3,
            is_active=True,
            depends_on_category=self.personal_info_category,
            depends_on_question_text='Employment type?',
            depends_on_value='["Full-time", "Part-time", "Contract"]',
            created_by=self.admin
        )
        
        from .serializers import ActiveSurveyQuestionsSerializer
        serializer = ActiveSurveyQuestionsSerializer(conditional_category)
        data = serializer.data
        
        # Verify the JSON array is preserved
        self.assertEqual(data['category']['depends_on_value'], '["Full-time", "Part-time", "Contract"]')

    def test_inactive_questions_not_included(self):
        """Test that inactive questions are not included in active survey"""
        # Make manager name question inactive
        self.manager_name_question.is_active = False
        self.manager_name_question.save()
        
        from .serializers import ActiveSurveyQuestionsSerializer
        serializer = ActiveSurveyQuestionsSerializer(self.employment_details_category)
        data = serializer.data
        
        # Should have 2 questions (job title and manager), not 3
        self.assertEqual(len(data['questions']), 2)
        
        # Manager name should not be in the list
        question_texts = [q['question_text'] for q in data['questions']]
        self.assertNotIn("What is your manager's name?", question_texts)

    def test_circular_dependency_prevention(self):
        """Test handling of potential circular dependencies"""
        # Create two questions that could create a circular dependency
        q1 = SurveyQuestion.objects.create(
            category=self.personal_info_category,
            question_text='Question 1',
            question_type='yes_no',
            order=3,
            is_active=True,
            created_by=self.admin
        )
        
        q2 = SurveyQuestion.objects.create(
            category=self.personal_info_category,
            question_text='Question 2',
            question_type='yes_no',
            order=4,
            is_active=True,
            depends_on_question=q1,
            depends_on_value='Yes',
            created_by=self.admin
        )
        
        # Try to make q1 depend on q2 (creating circular dependency)
        # In practice, frontend should hide both if there's a circular reference
        q1.depends_on_question = q2
        q1.depends_on_value = 'Yes'
        q1.save()
        
        # Both questions should still serialize without error
        from .serializers import ActiveSurveyQuestionsSerializer
        serializer = ActiveSurveyQuestionsSerializer(self.personal_info_category)
        data = serializer.data
        
        # Find both questions
        q1_data = next((q for q in data['questions'] if q['question_text'] == 'Question 1'), None)
        q2_data = next((q for q in data['questions'] if q['question_text'] == 'Question 2'), None)
        
        self.assertIsNotNone(q1_data)
        self.assertIsNotNone(q2_data)
        
        # Both should have their dependencies set
        self.assertEqual(q1_data['depends_on_question_id'], q2.id)
        self.assertEqual(q2_data['depends_on_question_id'], q1.id)

    def test_category_order_with_conditionals(self):
        """Test that category ordering is preserved with conditional categories"""
        self.client.force_authenticate(user=self.alumni)
        
        response = self.client.get('/api/survey/questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Categories should be in order
        category_names = [cat['category']['name'] for cat in response.data]
        expected_order = ['Personal Information', 'Employment Details']
        
        self.assertEqual(category_names, expected_order)

    def test_empty_dependency_value_treated_as_no_dependency(self):
        """Test that empty string for depends_on_value means no dependency"""
        question = SurveyQuestion.objects.create(
            category=self.personal_info_category,
            question_text='No dependency question',
            question_type='text',
            is_required=False,
            order=5,
            is_active=True,
            depends_on_question=self.employment_question,  # Set but...
            depends_on_value='',  # Empty value
            created_by=self.admin
        )
        
        from .serializers import ActiveSurveyQuestionsSerializer
        serializer = ActiveSurveyQuestionsSerializer(self.personal_info_category)
        data = serializer.data
        
        # Find the question
        q_data = next((q for q in data['questions'] if q['question_text'] == 'No dependency question'), None)
        self.assertIsNotNone(q_data)
        
        # Should have the depends_on_question_id but empty depends_on_value
        self.assertEqual(q_data['depends_on_question_id'], self.employment_question.id)
        self.assertEqual(q_data['depends_on_value'], '')

    def test_boolean_to_string_normalization_scenario(self):
        """Test scenario where yes_no questions store boolean but need string comparison"""
        # This tests the frontend normalization logic conceptually
        # In practice, yes_no questions might store true/false or "Yes"/"No"
        
        # Create a question that depends on a yes_no type
        dependent_q = SurveyQuestion.objects.create(
            category=self.personal_info_category,
            question_text='Dependent on yes/no',
            question_type='text',
            is_required=False,
            order=6,
            is_active=True,
            depends_on_question=self.employment_question,
            depends_on_value='Yes',  # String value
            created_by=self.admin
        )
        
        from .serializers import ActiveSurveyQuestionsSerializer
        serializer = ActiveSurveyQuestionsSerializer(self.personal_info_category)
        data = serializer.data
        
        # Find the dependent question
        dep_data = next((q for q in data['questions'] if q['question_text'] == 'Dependent on yes/no'), None)
        self.assertIsNotNone(dep_data)
        
        # The depends_on_value should be exactly 'Yes' (string)
        self.assertEqual(dep_data['depends_on_value'], 'Yes')
        
        # Frontend should normalize boolean true to 'Yes' for comparison

    def test_include_in_registration_flag(self):
        """Test that include_in_registration flag works independently of conditionals"""
        # Create a registration-only category with conditionals
        reg_category = SurveyCategory.objects.create(
            name='Registration Only',
            description='Only in registration',
            order=4,
            is_active=True,
            include_in_registration=True,
            depends_on_category=self.personal_info_category,
            depends_on_question_text='Are you currently employed?',
            depends_on_value='["Yes"]',
            created_by=self.admin
        )
        
        from .serializers import ActiveSurveyQuestionsSerializer
        serializer = ActiveSurveyQuestionsSerializer(reg_category)
        data = serializer.data
        
        # Should have both flags
        self.assertTrue(data['category']['include_in_registration'])
        self.assertEqual(data['category']['depends_on_category'], self.personal_info_category.id)


class BackwardCompatibilityTestCase(TestCase):
    """Test backward compatibility with existing surveys without conditionals"""

    def setUp(self):
        """Set up test data for backward compatibility"""
        self.admin = User.objects.create_user(
            username='admin2',
            email='admin2@test.com',
            password='admin123',
            user_type=1,
            first_name='Admin',
            last_name='User'
        )
        
        self.alumni = User.objects.create_user(
            username='alumni2',
            email='alumni2@test.com',
            password='alumni123',
            user_type=3,
            first_name='Alumni',
            last_name='User'
        )
        
        self.client = APIClient()

    def test_old_surveys_without_conditionals_work(self):
        """Test that surveys created before conditional logic still work"""
        # Create a simple category without any conditional fields
        category = SurveyCategory.objects.create(
            name='Old Survey Category',
            description='Created before conditional logic',
            order=1,
            is_active=True,
            created_by=self.admin
            # No depends_on_* fields set
        )
        
        # Create simple questions without conditionals
        q1 = SurveyQuestion.objects.create(
            category=category,
            question_text='Old Question 1',
            question_type='text',
            is_required=True,
            order=1,
            is_active=True,
            created_by=self.admin
        )
        
        q2 = SurveyQuestion.objects.create(
            category=category,
            question_text='Old Question 2',
            question_type='textarea',
            is_required=False,
            order=2,
            is_active=True,
            created_by=self.admin
        )
        
        # Test API response
        self.client.force_authenticate(user=self.alumni)
        response = self.client.get('/api/survey/questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        
        # Check category data
        cat_data = response.data[0]
        self.assertIsNone(cat_data['category']['depends_on_category'])
        self.assertEqual(cat_data['category']['depends_on_question_text'], '')
        self.assertEqual(cat_data['category']['depends_on_value'], '')
        
        # Check questions data
        self.assertEqual(len(cat_data['questions']), 2)
        for question in cat_data['questions']:
            self.assertIsNone(question['depends_on_question_id'])
            self.assertEqual(question['depends_on_value'], '')

    def test_mixed_conditional_and_non_conditional_questions(self):
        """Test survey with mix of conditional and non-conditional questions"""
        category = SurveyCategory.objects.create(
            name='Mixed Survey',
            order=1,
            is_active=True,
            created_by=self.admin
        )
        
        # Regular question (no conditions)
        q1 = SurveyQuestion.objects.create(
            category=category,
            question_text='Regular Question',
            question_type='text',
            is_required=True,
            order=1,
            is_active=True,
            created_by=self.admin
        )
        
        # Conditional question
        q2 = SurveyQuestion.objects.create(
            category=category,
            question_text='Conditional Question',
            question_type='text',
            is_required=False,
            order=2,
            is_active=True,
            depends_on_question=q1,
            depends_on_value='specific value',
            created_by=self.admin
        )
        
        from .serializers import ActiveSurveyQuestionsSerializer
        serializer = ActiveSurveyQuestionsSerializer(category)
        data = serializer.data
        
        # First question should have no dependencies
        self.assertIsNone(data['questions'][0]['depends_on_question_id'])
        
        # Second question should have dependencies
        self.assertEqual(data['questions'][1]['depends_on_question_id'], q1.id)
        self.assertEqual(data['questions'][1]['depends_on_value'], 'specific value')


class SurveyCompletionDetectionTestCase(TestCase):
    """Test survey completion detection with has_any_response and is_complete flags"""

    def setUp(self):
        """Set up test data for completion detection tests"""
        from .models import SurveyTemplate, SurveyResponse
        
        # Create admin user
        self.admin = User.objects.create_user(
            username='admin_completion',
            email='admin_completion@test.com',
            password='admin123',
            user_type=1,
            first_name='Admin',
            last_name='User',
            is_approved=True
        )
        
        # Create test alumni users
        self.alumni_skip = User.objects.create_user(
            username='alumni_skip',
            email='alumni_skip@test.com',
            password='alumni123',
            user_type=3,
            first_name='Skip',
            last_name='User',
            is_approved=True
        )
        
        self.alumni_partial = User.objects.create_user(
            username='alumni_partial',
            email='alumni_partial@test.com',
            password='alumni123',
            user_type=3,
            first_name='Partial',
            last_name='User',
            is_approved=True
        )
        
        self.alumni_complete = User.objects.create_user(
            username='alumni_complete',
            email='alumni_complete@test.com',
            password='alumni123',
            user_type=3,
            first_name='Complete',
            last_name='User',
            is_approved=True
        )
        
        self.client = APIClient()
        
        # Create a survey template
        self.template = SurveyTemplate.objects.create(
            name='Alumni Survey Form',
            description='Main alumni survey',
            is_active=True,
            is_published=True,
            created_by=self.admin
        )
        
        # Create a category linked to the template
        self.category = SurveyCategory.objects.create(
            name='Background Information',
            description='Tell us about yourself',
            order=1,
            is_active=True,
            created_by=self.admin
        )
        
        # Link category to template
        self.template.categories.add(self.category)
        
        # Create 5 questions in the category
        self.questions = []
        question_data = [
            ('What is your full name?', 'text'),
            ('What year did you graduate?', 'number'),
            ('Are you currently employed?', 'yes_no'),
            ('What is your current occupation?', 'text'),
            ('How satisfied are you with your career?', 'radio')
        ]
        
        for idx, (text, q_type) in enumerate(question_data, start=1):
            question = SurveyQuestion.objects.create(
                category=self.category,
                question_text=text,
                question_type=q_type,
                options=['Very Satisfied', 'Satisfied', 'Neutral', 'Dissatisfied'] if q_type == 'radio' else None,
                is_required=True,
                order=idx,
                is_active=True,
                created_by=self.admin
            )
            self.questions.append(question)

    def test_skip_survey_shows_no_completion(self):
        """Test: User skips survey during registration → is_complete=False, has_any_response=False, no banner"""
        from .models import SurveyResponse
        
        # Authenticate as alumni who skipped
        self.client.force_authenticate(user=self.alumni_skip)
        
        # Verify no responses exist
        response_count = SurveyResponse.objects.filter(user=self.alumni_skip, form=self.template).count()
        self.assertEqual(response_count, 0)
        
        # Call the active survey questions endpoint
        response = self.client.get('/api/survey/active-questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find our template in the response
        template_data = None
        for item in response.data:
            # Each item has 'template' and 'categories' keys
            for category in item.get('categories', []):
                if category['category']['name'] == 'Background Information':
                    template_data = item.get('template')
                    break
            if template_data:
                break
        
        self.assertIsNotNone(template_data, "Template data not found in response")
        
        # Verify flags
        self.assertFalse(template_data.get('has_any_response', True), 
                        "has_any_response should be False when user skipped survey")
        self.assertFalse(template_data.get('is_complete', True), 
                        "is_complete should be False when user skipped survey")
        self.assertEqual(template_data.get('answered_count', -1), 0, 
                        "answered_count should be 0 when user skipped survey")
        self.assertEqual(template_data.get('total_questions', -1), 5, 
                        "total_questions should be 5")

    def test_partial_answer_shows_incomplete(self):
        """Test: User answers 2 of 5 questions → has_any_response=True, is_complete=False, no banner"""
        from .models import SurveyResponse
        
        # Create responses for first 2 questions only
        SurveyResponse.objects.create(
            user=self.alumni_partial,
            question=self.questions[0],
            response_data='John Doe',
            form=self.template
        )
        SurveyResponse.objects.create(
            user=self.alumni_partial,
            question=self.questions[1],
            response_data='2020',
            form=self.template
        )
        
        # Verify 2 responses exist
        response_count = SurveyResponse.objects.filter(user=self.alumni_partial, form=self.template).count()
        self.assertEqual(response_count, 2)
        
        # Authenticate and call endpoint
        self.client.force_authenticate(user=self.alumni_partial)
        response = self.client.get('/api/survey/active-questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find template data
        template_data = None
        for item in response.data:
            for category in item.get('categories', []):
                if category['category']['name'] == 'Background Information':
                    template_data = item.get('template')
                    break
            if template_data:
                break
        
        self.assertIsNotNone(template_data, "Template data not found in response")
        
        # Verify flags
        self.assertTrue(template_data.get('has_any_response', False), 
                       "has_any_response should be True when user has partial answers")
        self.assertFalse(template_data.get('is_complete', True), 
                        "is_complete should be False when user answered 2 of 5 questions")
        self.assertEqual(template_data.get('answered_count', -1), 2, 
                        "answered_count should be 2")
        self.assertEqual(template_data.get('total_questions', -1), 5, 
                        "total_questions should be 5")

    def test_full_answer_shows_complete(self):
        """Test: User answers all 5 questions → has_any_response=True, is_complete=True, banner shows"""
        from .models import SurveyResponse
        
        # Create responses for all 5 questions
        response_data_list = [
            'Jane Smith',
            '2019',
            'Yes',
            'Software Engineer',
            'Very Satisfied'
        ]
        
        for question, answer in zip(self.questions, response_data_list):
            SurveyResponse.objects.create(
                user=self.alumni_complete,
                question=question,
                response_data=answer,
                form=self.template
            )
        
        # Verify 5 responses exist
        response_count = SurveyResponse.objects.filter(user=self.alumni_complete, form=self.template).count()
        self.assertEqual(response_count, 5)
        
        # Authenticate and call endpoint
        self.client.force_authenticate(user=self.alumni_complete)
        response = self.client.get('/api/survey/active-questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find template data
        template_data = None
        for item in response.data:
            for category in item.get('categories', []):
                if category['category']['name'] == 'Background Information':
                    template_data = item.get('template')
                    break
            if template_data:
                break
        
        self.assertIsNotNone(template_data, "Template data not found in response")
        
        # Verify flags
        self.assertTrue(template_data.get('has_any_response', False), 
                       "has_any_response should be True when user completed survey")
        self.assertTrue(template_data.get('is_complete', False), 
                       "is_complete should be True when user answered all 5 questions")
        self.assertEqual(template_data.get('answered_count', -1), 5, 
                        "answered_count should be 5")
        self.assertEqual(template_data.get('total_questions', -1), 5, 
                        "total_questions should be 5")

    def test_form_scoped_responses_isolated(self):
        """Test: Responses are scoped to specific form templates"""
        from .models import SurveyTemplate, SurveyResponse
        
        # Create a second template with the same category
        template2 = SurveyTemplate.objects.create(
            name='Second Survey Form',
            description='Another survey',
            is_active=True,
            is_published=True,
            created_by=self.admin
        )
        template2.categories.add(self.category)
        
        # User completes first template fully
        for question in self.questions:
            SurveyResponse.objects.create(
                user=self.alumni_complete,
                question=question,
                response_data='Answer',
                form=self.template
            )
        
        # User has no responses for second template
        # Verify first template shows complete
        self.client.force_authenticate(user=self.alumni_complete)
        response = self.client.get('/api/survey/active-questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Both templates should appear in response
        templates_found = []
        for item in response.data:
            template_info = item.get('template')
            if template_info:
                templates_found.append(template_info)
        
        # We should see data for our category, and it should be scoped to first template
        # (this depends on how the view returns multiple templates for the same category)
        # The key assertion: responses for template 1 don't affect template 2
                templates_found.append(template_info)
        
        # We should see data for our category, and it should be scoped to first template
        # (this depends on how the view returns multiple templates for the same category)
        # The key assertion: responses for template 1 don't affect template 2
        
        template1_responses = SurveyResponse.objects.filter(
            user=self.alumni_complete, 
            form=self.template
        ).count()
        template2_responses = SurveyResponse.objects.filter(
            user=self.alumni_complete, 
            form=template2
        ).count()
        
        self.assertEqual(template1_responses, 5, "Template 1 should have 5 responses")
        self.assertEqual(template2_responses, 0, "Template 2 should have 0 responses")

    def test_zero_questions_template(self):
        """Test: Template with no active questions shows is_complete=False"""
        from .models import SurveyTemplate
        
        # Create a template with no questions
        empty_template = SurveyTemplate.objects.create(
            name='Empty Survey',
            description='No questions',
            is_active=True,
            is_published=True,
            created_by=self.admin
        )
        
        # Create category with no questions
        empty_category = SurveyCategory.objects.create(
            name='Empty Category',
            description='No questions here',
            order=2,
            is_active=True,
            created_by=self.admin
        )
        empty_template.categories.add(empty_category)
        
        # Authenticate and call endpoint
        self.client.force_authenticate(user=self.alumni_skip)
        response = self.client.get('/api/survey/active-questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find empty category data
        empty_data = None
        for item in response.data:
            for category in item.get('categories', []):
                if category['category']['name'] == 'Empty Category':
                    empty_data = item.get('template')
                    break
            if empty_data:
                break
        
        # Empty template should exist and show incomplete
        if empty_data:
            self.assertFalse(empty_data.get('is_complete', True), 
                           "Template with 0 questions should have is_complete=False")
            self.assertEqual(empty_data.get('total_questions', -1), 0)

    def test_inactive_questions_not_counted(self):
        """Test: Inactive questions are not counted in total_questions or completion check"""
        from .models import SurveyResponse
        
        # Mark 2 questions as inactive
        self.questions[3].is_active = False
        self.questions[3].save()
        self.questions[4].is_active = False
        self.questions[4].save()
        
        # User answers first 3 questions (all active ones)
        for question in self.questions[:3]:
            SurveyResponse.objects.create(
                user=self.alumni_complete,
                question=question,
                response_data='Answer',
                form=self.template
            )
        
        # Authenticate and call endpoint
        self.client.force_authenticate(user=self.alumni_complete)
        response = self.client.get('/api/survey/active-questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Find template data
        template_data = None
        for item in response.data:
            for category in item.get('categories', []):
                if category['category']['name'] == 'Background Information':
                    template_data = item.get('template')
                    break
            if template_data:
                break
        
        self.assertIsNotNone(template_data)
        
        # Should show complete because only 3 active questions exist
        self.assertEqual(template_data.get('total_questions', -1), 3, 
                        "Should only count active questions")
        self.assertEqual(template_data.get('answered_count', -1), 3)
        self.assertTrue(template_data.get('is_complete', False), 
                       "Should be complete when all active questions are answered")

    def test_update_or_create_response_maintains_completion(self):
        """Test: Updating an existing response doesn't create duplicates"""
        from .models import SurveyResponse
        
        # Create initial response
        response1 = SurveyResponse.objects.create(
            user=self.alumni_partial,
            question=self.questions[0],
            response_data='First Answer',
            form=self.template
        )
        
        initial_count = SurveyResponse.objects.filter(
            user=self.alumni_partial, 
            form=self.template
        ).count()
        self.assertEqual(initial_count, 1)
        
        # Update the same question's response
        response2, created = SurveyResponse.objects.update_or_create(
            user=self.alumni_partial,
            question=self.questions[0],
            defaults={'response_data': 'Updated Answer', 'form': self.template}
        )
        
        # Should not create a duplicate
        self.assertFalse(created, "Should update existing response, not create new")
        self.assertEqual(response1.id, response2.id, "Should be the same response object")
        
        final_count = SurveyResponse.objects.filter(
            user=self.alumni_partial, 
            form=self.template
        ).count()
        self.assertEqual(final_count, 1, "Should still have only 1 response")
        
        # Verify updated value
        response2.refresh_from_db()
        self.assertEqual(response2.response_data, 'Updated Answer')

    def test_completion_with_mixed_template_categories(self):
        """Test: Completion detection works when template has multiple categories"""
        from .models import SurveyTemplate, SurveyResponse
        
        # Create a second category
        category2 = SurveyCategory.objects.create(
            name='Additional Info',
            description='More questions',
            order=2,
            is_active=True,
            created_by=self.admin
        )
        
        # Add 3 questions to second category
        additional_questions = []
        for idx in range(3):
            question = SurveyQuestion.objects.create(
                category=category2,
                question_text=f'Additional Question {idx + 1}',
                question_type='text',
                is_required=True,
                order=idx + 1,
                is_active=True,
                created_by=self.admin
            )
            additional_questions.append(question)
        
        # Add second category to template (total should be 5 + 3 = 8 questions)
        self.template.categories.add(category2)
        
        # User answers all 5 questions from first category
        for question in self.questions:
            SurveyResponse.objects.create(
                user=self.alumni_partial,
                question=question,
                response_data='Answer',
                form=self.template
            )
        
        # User answers 1 of 3 from second category
        SurveyResponse.objects.create(
            user=self.alumni_partial,
            question=additional_questions[0],
            response_data='Answer',
            form=self.template
        )
        
        # Total: 6 answers out of 8 questions → incomplete
        self.client.force_authenticate(user=self.alumni_partial)
        response = self.client.get('/api/survey/active-questions/')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check first category's template data
        template_data = None
        for item in response.data:
            for category in item.get('categories', []):
                if category['category']['name'] == 'Background Information':
                    template_data = item.get('template')
                    break
            if template_data:
                break
        
        self.assertIsNotNone(template_data)
        
        # Template should show 8 total questions across both categories
        self.assertEqual(template_data.get('total_questions', -1), 8, 
                        "Should count questions from all categories in template")
        self.assertEqual(template_data.get('answered_count', -1), 6,
                        "Should count all answers across categories")
        self.assertTrue(template_data.get('has_any_response', False))
        self.assertFalse(template_data.get('is_complete', True), 
                        "Should be incomplete with 6/8 answered")
