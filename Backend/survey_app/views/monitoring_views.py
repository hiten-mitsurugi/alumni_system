"""
Survey App - Monitoring Views
==============================
Views for monitoring survey responses and non-respondents (Problem 2).
These views allow admins/superadmins to track who hasn't responded to surveys.
"""

from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import HttpResponse
from django.utils import timezone
import csv

from ..models import SurveyTemplate
from ..serializers import NonRespondentSerializer, SurveyStatisticsSerializer
from ..permissions import IsSurveyAdmin
from ..utils import get_survey_non_respondents, get_survey_response_statistics


class SurveyNonRespondentsView(APIView):
    """
    GET /api/surveys/{survey_id}/non-respondents/
    
    Get list of alumni who have not responded to a specific survey.
    Supports filtering by program, year_graduated, etc.
    
    Query Parameters:
        - program: Filter by program name (case-insensitive partial match)
        - year_graduated: Filter by specific graduation year
        - year_graduated_from: Filter by graduation year range (from)
        - year_graduated_to: Filter by graduation year range (to)
        - export: If 'csv', download as CSV file
    """
    permission_classes = [IsSurveyAdmin]
    
    def get(self, request, survey_id):
        """Get non-respondents for a survey with optional filters"""
        try:
            survey = SurveyTemplate.objects.get(id=survey_id)
        except SurveyTemplate.DoesNotExist:
            return Response(
                {'error': 'Survey not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Build filters from query params
        filters = {}
        if request.query_params.get('program'):
            filters['program'] = request.query_params.get('program')
        if request.query_params.get('year_graduated'):
            filters['year_graduated'] = request.query_params.get('year_graduated')
        if request.query_params.get('year_graduated_from'):
            filters['year_graduated_from'] = request.query_params.get('year_graduated_from')
        if request.query_params.get('year_graduated_to'):
            filters['year_graduated_to'] = request.query_params.get('year_graduated_to')
        
        # Get non-respondents
        non_respondents = get_survey_non_respondents(survey, filters)
        
        # Check if export to CSV is requested
        if request.query_params.get('export') == 'csv':
            return self._export_to_csv(non_respondents, survey)
        
        # Serialize and return JSON response
        serializer = NonRespondentSerializer(non_respondents, many=True)
        
        # Get statistics
        stats = get_survey_response_statistics(survey)
        
        return Response({
            'survey': {
                'id': survey.id,
                'name': survey.name,
                'description': survey.description,
            },
            'statistics': stats,
            'non_respondents': serializer.data,
            'count': non_respondents.count(),
            'filters_applied': filters
        })
    
    def _export_to_csv(self, non_respondents, survey):
        """Export non-respondents to CSV file"""
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="non_respondents_{survey.id}_{timezone.now().strftime("%Y%m%d")}.csv"'
        
        writer = csv.writer(response)
        
        # Write header
        writer.writerow([
            'ID',
            'Email',
            'First Name',
            'Last Name',
            'Program',
            'Year Graduated',
            'Contact Number',
            'Last Login',
            'Date Joined'
        ])
        
        # Write data rows
        for user in non_respondents:
            writer.writerow([
                user.id,
                user.email,
                user.first_name,
                user.last_name,
                user.program or '',
                user.year_graduated or '',
                user.contact_number or '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S')
            ])
        
        return response


class SurveyStatisticsView(APIView):
    """
    GET /api/surveys/{survey_id}/statistics/
    
    Get response statistics for a specific survey.
    Shows total alumni, respondents, non-respondents, and response rate.
    """
    permission_classes = [IsSurveyAdmin]
    
    def get(self, request, survey_id):
        """Get statistics for a survey"""
        try:
            survey = SurveyTemplate.objects.get(id=survey_id)
        except SurveyTemplate.DoesNotExist:
            return Response(
                {'error': 'Survey not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get statistics
        stats = get_survey_response_statistics(survey)
        stats['survey_id'] = survey.id
        stats['survey_name'] = survey.name
        
        # Serialize
        serializer = SurveyStatisticsSerializer(stats)
        
        return Response(serializer.data)


class AllSurveysStatisticsView(APIView):
    """
    GET /api/surveys/statistics/all/
    
    Get response statistics for all published surveys.
    Useful for dashboard overview.
    """
    permission_classes = [IsSurveyAdmin]
    
    def get(self, request):
        """Get statistics for all surveys"""
        surveys = SurveyTemplate.objects.filter(
            is_published=True,
            is_active=True
        ).order_by('-created_at')
        
        all_stats = []
        for survey in surveys:
            stats = get_survey_response_statistics(survey)
            stats['survey_id'] = survey.id
            stats['survey_name'] = survey.name
            all_stats.append(stats)
        
        # Serialize
        serializer = SurveyStatisticsSerializer(all_stats, many=True)
        
        return Response({
            'count': len(all_stats),
            'results': serializer.data
        })
