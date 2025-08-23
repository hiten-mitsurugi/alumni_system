from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Count, Q
from django.utils import timezone
from django.core.cache import cache

from .models import SurveyCategory, SurveyQuestion, SurveyResponse, SurveyTemplate
from .serializers import (
    SurveyCategorySerializer, SurveyQuestionSerializer, SurveyQuestionListSerializer,
    SurveyResponseSerializer, SurveyResponseSubmissionSerializer,
    ActiveSurveyQuestionsSerializer, SurveyAnalyticsSerializer,
    SurveyTemplateSerializer
)
from .permissions import IsSurveyAdmin, IsSuperAdminOnly, CanRespondToSurveys, IsSurveyOwnerOrAdmin


# =============================================================================
# ADMIN VIEWS - Survey Management (Super Admin & Admin Only)
# =============================================================================

class SurveyCategoryListCreateView(generics.ListCreateAPIView):
    """
    List all survey categories or create a new one.
    Only admins can access this endpoint.
    """
    serializer_class = SurveyCategorySerializer
    permission_classes = [IsSurveyAdmin]
    
    def get_queryset(self):
        return SurveyCategory.objects.all().order_by('order', 'name')


class SurveyCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a survey category.
    Only super admins can delete categories.
    """
    serializer_class = SurveyCategorySerializer
    queryset = SurveyCategory.objects.all()
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsSuperAdminOnly()]
        return [IsSurveyAdmin()]


class SurveyQuestionListCreateView(generics.ListCreateAPIView):
    """
    List all survey questions or create a new one.
    Supports filtering by category and active status.
    """
    serializer_class = SurveyQuestionSerializer
    permission_classes = [IsSurveyAdmin]
    
    def get_queryset(self):
        queryset = SurveyQuestion.objects.select_related('category', 'created_by')
        
        # Filter by category
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset.order_by('category__order', 'order', 'question_text')


class SurveyQuestionDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a survey question.
    Only super admins can delete questions.
    """
    serializer_class = SurveyQuestionSerializer
    queryset = SurveyQuestion.objects.all()
    
    def get_permissions(self):
        if self.request.method == 'DELETE':
            return [IsSuperAdminOnly()]
        return [IsSurveyAdmin()]


class SurveyResponseAnalyticsView(APIView):
    """
    Provide analytics data for survey responses.
    Admin-only endpoint for viewing survey statistics.
    """
    permission_classes = [IsSurveyAdmin]
    
    def get(self, request):
        cache_key = 'survey_analytics_data'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Calculate analytics
        total_questions = SurveyQuestion.objects.filter(is_active=True).count()
        total_responses = SurveyResponse.objects.count()
        total_users_responded = SurveyResponse.objects.values('user').distinct().count()
        
        # Calculate completion rate
        from django.contrib.auth import get_user_model
        User = get_user_model()
        total_alumni = User.objects.filter(user_type=3, is_approved=True).count()
        completion_rate = (total_users_responded / total_alumni * 100) if total_alumni > 0 else 0
        
        # Category statistics
        category_stats = []
        for category in SurveyCategory.objects.filter(is_active=True):
            questions_count = category.questions.filter(is_active=True).count()
            responses_count = SurveyResponse.objects.filter(
                question__category=category
            ).count()
            category_stats.append({
                'name': category.name,
                'questions_count': questions_count,
                'responses_count': responses_count,
                'response_rate': (responses_count / (questions_count * total_alumni) * 100) if questions_count > 0 and total_alumni > 0 else 0
            })
        
        # Question statistics (top 10 most answered)
        question_stats = []
        top_questions = SurveyQuestion.objects.filter(is_active=True).annotate(
            response_count=Count('responses')
        ).order_by('-response_count')[:10]
        
        for question in top_questions:
            question_stats.append({
                'id': question.id,
                'question_text': question.question_text[:50] + '...' if len(question.question_text) > 50 else question.question_text,
                'category': question.category.name,
                'response_count': question.response_count,
                'response_rate': (question.response_count / total_alumni * 100) if total_alumni > 0 else 0
            })
        
        analytics_data = {
            'total_questions': total_questions,
            'total_responses': total_responses,
            'total_users_responded': total_users_responded,
            'completion_rate': round(completion_rate, 2),
            'category_stats': category_stats,
            'question_stats': question_stats,
            'generated_at': timezone.now().isoformat()
        }
        
        # Cache for 1 hour
        cache.set(cache_key, analytics_data, 3600)
        
        return Response(analytics_data)


class SurveyResponsesView(generics.ListAPIView):
    """
    List all survey responses for admin review.
    Supports filtering by user, question, and category.
    """
    serializer_class = SurveyResponseSerializer
    permission_classes = [IsSurveyAdmin]
    
    def get_queryset(self):
        queryset = SurveyResponse.objects.select_related(
            'user', 'question', 'question__category'
        )
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by question
        question_id = self.request.query_params.get('question_id')
        if question_id:
            queryset = queryset.filter(question_id=question_id)
        
        # Filter by category
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(question__category_id=category_id)
        
        return queryset.order_by('-submitted_at')


# =============================================================================
# ALUMNI VIEWS - Survey Taking (Alumni & Authenticated Users)
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
        # Check if it's bulk submission
        if 'responses' in request.data:
            serializer = SurveyResponseSubmissionSerializer(
                data=request.data,
                context={'request': request, 'ip_address': self.get_client_ip(request)}
            )
        else:
            # Single response submission
            serializer = SurveyResponseSerializer(
                data=request.data,
                context={'request': request}
            )
        
        if serializer.is_valid():
            response = serializer.save()
            
            # Clear user's cache
            cache_key = f'active_survey_questions_user_{request.user.id}'
            cache.delete(cache_key)
            cache.delete('survey_analytics_data')  # Clear analytics cache
            
            return Response(
                {'message': 'Survey response(s) submitted successfully'},
                status=status.HTTP_201_CREATED
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')


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
# UTILITY VIEWS
# =============================================================================

@api_view(['GET'])
@permission_classes([IsSurveyAdmin])
def survey_export_view(request):
    """
    Export survey data in various formats.
    Admin-only endpoint for data export.
    """
    export_format = request.query_params.get('format', 'json')
    
    if export_format not in ['json', 'csv']:
        return Response(
            {'error': 'Supported formats: json, csv'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Get all responses with related data
    responses = SurveyResponse.objects.select_related(
        'user', 'question', 'question__category'
    ).all()
    
    if export_format == 'json':
        serializer = SurveyResponseSerializer(responses, many=True)
        return Response({
            'export_format': 'json',
            'total_responses': len(responses),
            'responses': serializer.data,
            'exported_at': timezone.now().isoformat()
        })
    
    # CSV export would be implemented here
    return Response({'message': 'CSV export not yet implemented'})


@api_view(['POST'])
@permission_classes([IsSuperAdminOnly])
def clear_survey_cache_view(request):
    """
    Clear all survey-related cache.
    Super admin only utility endpoint.
    """
    cache_keys = [
        'survey_analytics_data',
        'active_survey_questions_user_*',  # Pattern
    ]
    
    # Clear specific cache keys
    cache.delete('survey_analytics_data')
    
    # Clear user-specific caches (would need more sophisticated cache management)
    # For now, we'll just clear the analytics cache
    
    return Response({
        'message': 'Survey cache cleared successfully',
        'cleared_at': timezone.now().isoformat()
    })


class RegistrationSurveyQuestionsView(APIView):
    """
    Get survey questions specifically for registration process.
    Public endpoint (no authentication required for registration).
    """
    permission_classes = [AllowAny]
    
    def get(self, request):
        cache_key = 'registration_survey_questions'
        cached_data = cache.get(cache_key)
        
        if cached_data:
            return Response(cached_data)
        
        # Get active categories with their questions
        # Filter out categories that should not be in registration (e.g., Personal Info, Alumni Verification)
        excluded_categories = ['Alumni Verification', 'Personal & Demographic Information']
        
        categories = SurveyCategory.objects.filter(
            is_active=True
        ).exclude(
            name__in=excluded_categories
        ).prefetch_related(
            'questions'
        ).order_by('order', 'name')
        
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
                    
                    # Add question-level conditional logic if exists
                    if question.depends_on_question:
                        question_data['depends_on_question'] = question.depends_on_question.id
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
                
                # Add category-level conditional logic if exists
                if category.depends_on_category:
                    category_data['category']['depends_on_category'] = category.depends_on_category.id
                    category_data['category']['depends_on_category_name'] = category.depends_on_category.name
                    category_data['category']['depends_on_question_text'] = category.depends_on_question_text
                    category_data['category']['depends_on_value'] = category.depends_on_value
                
                survey_data.append(category_data)
        
        # Cache for 30 minutes
        cache.set(cache_key, survey_data, 1800)
        
        return Response(survey_data)
