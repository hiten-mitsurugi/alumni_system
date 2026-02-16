"""
Survey App - Alumni-Facing Views
================================
Views for alumni to take surveys, view their progress, and submit responses.
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator

from ..models import SurveyCategory, SurveyQuestion, SurveyResponse, SurveyTemplate
from ..serializers import (
    SurveyCategorySerializer,
    ActiveSurveyQuestionsSerializer,
    SurveyResponseSerializer,
    SurveyResponseSubmissionSerializer
)
from ..permissions import CanRespondToSurveys


# =============================================================================
# SURVEY TAKING
# =============================================================================

class ActiveSurveyQuestionsView(APIView):
    """
    Get all published/active survey forms (templates) with their categories and questions.
    Alumni use this to see what surveys they can fill out.
    """
    permission_classes = [CanRespondToSurveys]
    
    def get(self, request):
        cache_key = f'active_survey_questions_user_{request.user.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Auto-expire any templates whose end date has passed
        from ..models import SurveyTemplate as ST
        ST.bulk_expire()

        # Get published and active templates (forms)
        templates = SurveyTemplate.objects.filter(
            is_active=True,
            is_published=True,
            accepting_responses=True
        ).prefetch_related(
            'categories',
            'categories__questions'
        ).order_by('name')
        
        survey_data = []
        for template in templates:
            # Get categories for this template (form)
            categories = template.categories.filter(is_active=True).order_by(
                'surveytemplatecategory__order', 'order', 'name'
            )
            
            # Check user's response status for this template (form)
            allow_multiple = template.form_settings.get('allow_multiple_responses', False) if template.form_settings else False
            
            # Count total active questions in this template
            total_questions = 0
            for cat in categories:
                total_questions += cat.questions.filter(is_active=True).count()
            
            # Count user's responses (prefer form-scoped if available, fallback to category-based)
            category_ids = list(categories.values_list('id', flat=True))
            
            # Try form-scoped query first (for new responses that set the form FK)
            form_responses = SurveyResponse.objects.filter(
                user=request.user,
                form=template
            )
            
            if form_responses.exists():
                # Use form-scoped responses (most accurate)
                answered_count = form_responses.count()
            else:
                # Fallback to category-based (for legacy responses without form FK)
                answered_count = SurveyResponse.objects.filter(
                    user=request.user,
                    question__category_id__in=category_ids
                ).count()
            
            # Determine completion status
            has_any_response = answered_count > 0
            is_complete = (answered_count >= total_questions) and total_questions > 0
            
            # Calculate visible questions based on conditional logic and user's responses
            from ..utils import calculate_visible_questions_for_user
            visibility_info = calculate_visible_questions_for_user(template, request.user)
            
            template_categories = []
            for category in categories:
                active_questions = category.questions.filter(is_active=True).order_by('order', 'question_text')
                
                if active_questions.exists():
                    questions_data = ActiveSurveyQuestionsSerializer(
                        active_questions, 
                        many=True, 
                        context={'request': request}
                    ).data
                    
                    template_categories.append({
                        'category': SurveyCategorySerializer(category).data,
                        'questions': questions_data
                    })
            
            # Only include templates that have categories with questions
            if template_categories:
                survey_data.append({
                    'template': {
                        'id': template.id,
                        'name': template.name,
                        'description': template.description,
                        'allow_multiple_responses': allow_multiple,
                        'has_answered': has_any_response,  # Keep for backward compatibility
                        'has_any_response': has_any_response,  # New: any response exists
                        'is_complete': is_complete,  # Old: all raw questions answered
                        'answered_count': answered_count,
                        'total_questions': total_questions,
                        # New conditional logic fields
                        'visible_questions': visibility_info['visible_questions'],
                        'answered_visible': visibility_info['answered_visible'],
                        'branching_complete': visibility_info['branching_complete'],
                    },
                    'categories': template_categories
                })
        
        # Cache for 5 minutes (300 seconds) - short enough to see changes quickly
        cache.set(cache_key, survey_data, 300)
        
        return Response(survey_data)


class SurveyResponseSubmitView(APIView):
    """
    Submit survey responses (single or multiple).
    Alumni use this to submit their survey answers.
    """
    permission_classes = [CanRespondToSurveys]
    
    def post(self, request):
        # Debug logging
        print(f"🚀 Survey submission received from user: {request.user}")
        print(f"📋 Request data: {request.data}")
        print(f"📊 Data type: {type(request.data)}")
        
        # Validate allow_multiple_responses enforcement
        if 'responses' in request.data and request.data['responses']:
            # Get the first question to identify which template (form) this belongs to
            first_response = request.data['responses'][0]
            question_id = first_response.get('question_id')
            
            if question_id:
                try:
                    question = SurveyQuestion.objects.select_related('category').get(id=question_id)
                    
                    # Find the template (form) this question belongs to
                    template = SurveyTemplate.objects.filter(
                        categories=question.category,
                        is_active=True
                    ).first()
                    
                    if template:
                        # Check allow_multiple_responses setting
                        allow_multiple = template.form_settings.get('allow_multiple_responses', False) if template.form_settings else False
                        
                        if not allow_multiple:
                            # Check if user already has responses for this template
                            category_ids = list(template.categories.values_list('id', flat=True))
                            has_existing_response = SurveyResponse.objects.filter(
                                user=request.user,
                                question__category_id__in=category_ids
                            ).exists()
                            
                            if has_existing_response:
                                return Response(
                                    {
                                        'error': 'You have already answered this form.',
                                        'message': 'This form does not allow multiple responses. You have already submitted your answers.'
                                    },
                                    status=status.HTTP_400_BAD_REQUEST
                                )
                
                except SurveyQuestion.DoesNotExist:
                    pass  # Continue with normal validation
        
        # Check if it's bulk submission
        if 'responses' in request.data:
            print("📦 Processing as bulk submission")
            serializer = SurveyResponseSubmissionSerializer(
                data=request.data,
                context={'request': request, 'ip_address': self.get_client_ip(request)}
            )
        else:
            print("📝 Processing as single response")
            serializer = SurveyResponseSerializer(
                data=request.data,
                context={'request': request}
            )
        
        if serializer.is_valid():
            print("✅ Serializer validation passed")
            response = serializer.save()
            print(f"✅ Response saved successfully: {response}")
            
            # Clear user's cache
            cache_key = f'active_survey_questions_user_{request.user.id}'
            cache.delete(cache_key)
            cache.delete('survey_analytics_data')
            
            return Response(
                {'message': 'Survey response(s) submitted successfully'},
                status=status.HTTP_201_CREATED
            )
        
        print(f"❌ Serializer validation failed: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


# =============================================================================
# USER PROGRESS & RESPONSES
# =============================================================================

class UserSurveyResponsesView(generics.ListAPIView):
    """
    Get current user's survey responses.
    Alumni can view their own submitted responses.
    """
    serializer_class = SurveyResponseSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return SurveyResponse.objects.filter(
            user=self.request.user
        ).select_related('question', 'question__category').order_by('-submitted_at')


class SurveyProgressView(APIView):
    """
    Get user's survey completion progress.
    Shows how many questions they've answered vs total questions.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get total active questions
        total_questions = SurveyQuestion.objects.filter(is_active=True).count()
        
        # Get user's responses count
        answered_questions = SurveyResponse.objects.filter(user=user).count()
        
        # Calculate progress percentage
        progress_percentage = (answered_questions / total_questions * 100) if total_questions > 0 else 0
        
        # Get category-wise progress
        category_progress = []
        for category in SurveyCategory.objects.filter(is_active=True):
            category_questions = category.questions.filter(is_active=True).count()
            category_answered = SurveyResponse.objects.filter(
                user=user, 
                question__category=category
            ).count()
            category_progress.append({
                'category_name': category.name,
                'total_questions': category_questions,
                'answered_questions': category_answered,
                'progress_percentage': (category_answered / category_questions * 100) if category_questions > 0 else 0
            })
        
        return Response({
            'total_questions': total_questions,
            'answered_questions': answered_questions,
            'progress_percentage': round(progress_percentage, 2),
            'category_progress': category_progress,
            'is_complete': answered_questions >= total_questions
        })


# =============================================================================
# REGISTRATION SURVEY
# =============================================================================

@method_decorator(never_cache, name='dispatch')
class RegistrationSurveyQuestionsView(APIView):
    """
    Get survey questions specifically for registration process.
    Public endpoint (no authentication required for registration).
    NO CACHING - Always fetch fresh data from database.
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        print(f"🔄 Loading registration survey form (template-based) from database")
        print(f"📥 Request params: {request.query_params}")

        # Choose the form (SurveyTemplate) for registration
        form_id = request.query_params.get('form_id')
        template = None

        if form_id:
            print(f"🔍 Looking for form with ID: {form_id}")
            try:
                template = SurveyTemplate.objects.get(id=form_id, is_active=True)
                print(f"✅ Found template by ID: {template.name}")
            except SurveyTemplate.DoesNotExist:
                print(f"❌ Template with ID {form_id} not found")
                return Response({'error': 'Registration form not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            print(f"🔍 Looking for default template (is_default=True, is_active=True)")
            all_templates = SurveyTemplate.objects.all()
            print(f"📊 Total templates in DB: {all_templates.count()}")
            for t in all_templates:
                print(f"  - Template {t.id}: {t.name}, is_active={t.is_active}, is_default={t.is_default}")
            
            template = SurveyTemplate.objects.filter(is_active=True, is_default=True).first()
            if template:
                print(f"✅ Found default template: {template.name}")
            else:
                print(f"❌ No default template found")

        if not template:
            print("⚠️ No default registration form configured")
            response = Response([])
            response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
            return response

        # Get categories from the selected template
        categories = template.categories.filter(is_active=True).prefetch_related('questions').order_by(
            'surveytemplatecategory__order', 'order', 'name'
        )

        survey_data = []
        for category in categories:
            active_questions = category.questions.filter(is_active=True).order_by('order', 'question_text')

            if active_questions.exists():
                questions_data = []
                for question in active_questions:
                    question_data = {
                        'id': question.id,
                        'question_text': question.question_text,
                        'question_type': question.question_type,
                        'placeholder_text': question.placeholder_text,
                        'help_text': question.help_text,
                        'options': question.get_options_list(),
                        'is_required': question.is_required,
                        'min_value': question.min_value,
                        'max_value': question.max_value,
                        'max_length': question.max_length,
                        'order': question.order
                    }

                    # Question-level conditional logic
                    if question.depends_on_question:
                        question_data['depends_on_question_id'] = question.depends_on_question.id
                        question_data['depends_on_value'] = question.depends_on_value

                    questions_data.append(question_data)

                category_data = {
                    'category': {
                        'id': category.id,
                        'name': category.name,
                        'description': category.description,
                        'page_title': category.page_title,
                        'page_description': category.page_description,
                        'order': category.order
                    },
                    'questions': questions_data
                }

                # Category-level conditional logic
                if category.depends_on_category:
                    category_data['category']['depends_on_category'] = category.depends_on_category.id
                    category_data['category']['depends_on_category_name'] = category.depends_on_category.name
                    category_data['category']['depends_on_question_text'] = category.depends_on_question_text
                    category_data['category']['depends_on_value'] = category.depends_on_value

                survey_data.append(category_data)

        # Return fresh data (no caching)
        print(f"✅ Returning registration form '{template.name}' with {len(survey_data)} categories")

        response = Response(survey_data)
        response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response['Pragma'] = 'no-cache'
        response['Expires'] = '0'
        return response
