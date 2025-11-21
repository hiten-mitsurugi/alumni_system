"""
Survey App - Distribution Views
================================
Views for public survey access via shared links.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.utils import timezone
from django.shortcuts import get_object_or_404

from ..models import SurveyTemplate, SurveyQuestion, SurveyResponse
from ..serializers import SurveyCategorySerializer, SurveyQuestionSerializer


class PublicSurveyDetailView(APIView):
    """
    GET /api/surveys/public/<slug>/
    
    PUBLIC endpoint - Get survey details by slug for alumni to take the survey.
    No authentication required.
    Returns the full survey structure with categories and questions.
    """
    permission_classes = [AllowAny]
    
    def get(self, request, slug):
        """
        Retrieve published survey by slug with full structure.
        Checks:
        1. If survey requires login and user is not authenticated
        2. If user already completed the survey
        """
        # Find survey by public_slug or by name-based slug
        survey = None
        
        # Try to find by public_slug first
        try:
            survey = SurveyTemplate.objects.get(
                public_slug=slug,
                is_published=True,
                is_active=True
            )
        except SurveyTemplate.DoesNotExist:
            # Try to match by name-based slug
            all_surveys = SurveyTemplate.objects.filter(
                is_published=True,
                is_active=True
            )
            for s in all_surveys:
                name_slug = s.name.lower().replace(' ', '-').replace('(', '').replace(')', '').replace(',', '')
                # Remove special characters
                import re
                name_slug = re.sub(r'[^a-z0-9-]', '', name_slug)
                if name_slug == slug:
                    survey = s
                    break
        
        if not survey:
            return Response({
                'error': 'Survey not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if survey requires login
        form_settings = survey.form_settings or {}
        require_login = form_settings.get('require_login', False)
        
        if require_login and not request.user.is_authenticated:
            return Response({
                'error': 'login_required',
                'message': 'You need to login to access this survey'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if authenticated user already completed this survey
        has_completed = False
        submitted_at = None
        
        if request.user.is_authenticated:
            # Check for existing responses from this user for this survey
            existing_response = SurveyResponse.objects.filter(
                user=request.user,
                question__category__in=survey.categories.all()
            ).first()
            
            if existing_response:
                has_completed = True
                submitted_at = existing_response.submitted_at
                
                # Check if multiple responses are allowed
                allow_multiple = form_settings.get('allow_multiple_responses', False)
                
                if not allow_multiple:
                    return Response({
                        'error': 'already_completed',
                        'message': 'You have already completed this survey',
                        'submitted_at': submitted_at
                    }, status=status.HTTP_403_FORBIDDEN)
        
        # Build response with full structure (same as admin form detail view)
        survey_data = {
            'id': survey.id,
            'name': survey.name,
            'description': survey.description,
            'is_published': survey.is_published,
            'accepting_responses': survey.accepting_responses,
            'start_at': survey.start_at,
            'end_at': survey.end_at,
            'confirmation_message': survey.confirmation_message,
            'has_completed': has_completed,
            'submitted_at': submitted_at,
        }
        
        # Add categories with their questions (sections structure)
        categories = survey.categories.all().order_by('surveytemplatecategory__order', 'order', 'name')
        sections = []
        
        for cat in categories:
            questions = SurveyQuestion.objects.filter(
                category=cat,
                is_active=True
            ).order_by('order', 'question_text')
            
            sections.append({
                'category': SurveyCategorySerializer(cat).data,
                'questions': SurveyQuestionSerializer(questions, many=True).data
            })
        
        survey_data['sections'] = sections
        survey_data['categories'] = [s['category'] for s in sections]
        
        return Response(survey_data)
