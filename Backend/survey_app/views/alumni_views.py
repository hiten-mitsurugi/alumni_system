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
    Get all active survey questions organized by categories.
    Alumni use this to see what surveys they can fill out.
    """
    permission_classes = [CanRespondToSurveys]
    
    def get(self, request):
        cache_key = f'active_survey_questions_user_{request.user.id}'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get active categories with their questions
        categories = SurveyCategory.objects.filter(is_active=True).prefetch_related(
            'questions'
        ).order_by('order', 'name')
        
        survey_data = []
        for category in categories:
            active_questions = category.questions.filter(is_active=True).order_by('order', 'question_text')
            
            if active_questions.exists():
                questions_data = ActiveSurveyQuestionsSerializer(
                    active_questions, 
                    many=True, 
                    context={'request': request}
                ).data
                
                survey_data.append({
                    'category': SurveyCategorySerializer(category).data,
                    'questions': questions_data
                })
        
        # Cache for 30 minutes
        cache.set(cache_key, survey_data, 1800)
        
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
