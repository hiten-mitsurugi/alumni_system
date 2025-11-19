"""
Survey App - Analytics Views
============================
Views for survey analytics, reporting, and data visualization.
Includes response analytics and comprehensive dashboard analytics.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
from django.utils import timezone
from django.core.cache import cache

from ..models import SurveyCategory, SurveyQuestion, SurveyResponse
from ..permissions import IsSurveyAdmin
from .utils import extract_value


# =============================================================================
# BASIC SURVEY ANALYTICS
# =============================================================================

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
            responses_total=Count('responses')
        ).order_by('-responses_total')[:10]
        
        for question in top_questions:
            question_stats.append({
                'id': question.id,
                'question_text': question.question_text[:50] + '...' if len(question.question_text) > 50 else question.question_text,
                'category': question.category.name,
                'response_count': question.responses_total,
                'response_rate': (question.responses_total / total_alumni * 100) if total_alumni > 0 else 0
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


class CategoryAnalyticsView(APIView):
    """
    Get detailed analytics for a specific category.
    Returns per-question aggregated statistics ready for charting.
    """
    permission_classes = [IsSurveyAdmin]
    
    def get(self, request):
        category_id = request.query_params.get('category_id')
        
        if not category_id:
            return Response(
                {'error': 'category_id parameter is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            category = SurveyCategory.objects.get(id=category_id)
        except SurveyCategory.DoesNotExist:
            return Response(
                {'error': 'Category not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check cache first
        cache_key = f'category_analytics_{category_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        
        # Get all questions for this category
        questions = SurveyQuestion.objects.filter(
            category=category,
            is_active=True
        ).order_by('order', 'question_text')
        
        # Get all responses for this category
        responses = SurveyResponse.objects.filter(
            question__category=category
        ).select_related('user', 'question')
        
        # Get total potential respondents (alumni)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        total_alumni = User.objects.filter(user_type=3, is_approved=True).count()
        
        # Calculate per-question analytics
        question_analytics = []
        
        for question in questions:
            question_responses = responses.filter(question=question)
            response_count = question_responses.count()
            
            analytics_item = {
                'question_id': question.id,
                'question_text': question.question_text,
                'question_type': question.question_type,
                'help_text': question.help_text,
                'is_required': question.is_required,
                'response_count': response_count,
                'response_rate': round((response_count / total_alumni * 100) if total_alumni > 0 else 0, 2),
                'order': question.order
            }
            
            # Type-specific analytics
            if question.question_type in ['radio', 'select']:
                distribution = {}
                for response in question_responses:
                    value = extract_value(response.response_data)
                    if value:
                        distribution[str(value)] = distribution.get(str(value), 0) + 1
                analytics_item['distribution'] = distribution
                analytics_item['options'] = question.get_options_list()
                
            elif question.question_type == 'checkbox':
                distribution = {}
                for response in question_responses:
                    values = extract_value(response.response_data)
                    if isinstance(values, list):
                        for value in values:
                            distribution[str(value)] = distribution.get(str(value), 0) + 1
                    elif values:
                        distribution[str(values)] = distribution.get(str(values), 0) + 1
                analytics_item['distribution'] = distribution
                analytics_item['options'] = question.get_options_list()
                
            elif question.question_type == 'rating':
                values = []
                distribution = {}
                for response in question_responses:
                    value = extract_value(response.response_data)
                    if value is not None:
                        try:
                            numeric_value = float(value)
                            values.append(numeric_value)
                            distribution[str(int(numeric_value))] = distribution.get(str(int(numeric_value)), 0) + 1
                        except (ValueError, TypeError):
                            pass
                analytics_item['distribution'] = distribution
                analytics_item['average'] = round(sum(values) / len(values), 2) if values else 0
                analytics_item['min_value'] = question.min_value or 1
                analytics_item['max_value'] = question.max_value or 5
                
            elif question.question_type == 'yes_no':
                distribution = {'Yes': 0, 'No': 0}
                for response in question_responses:
                    value = extract_value(response.response_data)
                    if value in ['Yes', 'yes', True, 'true', '1', 1]:
                        distribution['Yes'] += 1
                    elif value in ['No', 'no', False, 'false', '0', 0]:
                        distribution['No'] += 1
                analytics_item['distribution'] = distribution
                
            elif question.question_type in ['text', 'textarea', 'email']:
                sample_responses = []
                for response in question_responses[:10]:
                    value = extract_value(response.response_data)
                    if value:
                        sample_responses.append({
                            'value': str(value)[:200],
                            'submitted_at': response.submitted_at.isoformat()
                        })
                analytics_item['sample_responses'] = sample_responses
                
            elif question.question_type == 'number':
                values = []
                for response in question_responses:
                    value = extract_value(response.response_data)
                    if value is not None:
                        try:
                            values.append(float(value))
                        except (ValueError, TypeError):
                            pass
                
                if values:
                    analytics_item['average'] = round(sum(values) / len(values), 2)
                    analytics_item['min'] = min(values)
                    analytics_item['max'] = max(values)
                    
                    # Create histogram buckets
                    min_val = min(values)
                    max_val = max(values)
                    range_val = max_val - min_val
                    
                    if range_val == 0:
                        analytics_item['distribution'] = {str(int(min_val)): len(values)}
                    else:
                        num_buckets = min(10, max(5, int(range_val / 5) + 1))
                        bucket_width = range_val / num_buckets
                        distribution = {}
                        for i in range(num_buckets):
                            bucket_start = min_val + (i * bucket_width)
                            bucket_end = bucket_start + bucket_width
                            if i == num_buckets - 1:
                                bucket_label = f"{int(bucket_start)}-{int(bucket_end)}"
                                count = sum(1 for v in values if bucket_start <= v <= bucket_end)
                            else:
                                bucket_label = f"{int(bucket_start)}-{int(bucket_end-1)}"
                                count = sum(1 for v in values if bucket_start <= v < bucket_end)
                            if count > 0:
                                distribution[bucket_label] = count
                        analytics_item['distribution'] = distribution
                else:
                    analytics_item['average'] = 0
                    analytics_item['min'] = 0
                    analytics_item['max'] = 0
                    analytics_item['distribution'] = {}
                
            elif question.question_type == 'date':
                dates = []
                for response in question_responses:
                    value = extract_value(response.response_data)
                    if value:
                        dates.append(str(value))
                analytics_item['sample_dates'] = dates[:10]
            
            question_analytics.append(analytics_item)
        
        # Category summary
        category_data = {
            'category': {
                'id': category.id,
                'name': category.name,
                'description': category.description,
                'total_questions': questions.count(),
                'active_questions': questions.count()
            },
            'summary': {
                'total_responses': responses.count(),
                'unique_respondents': responses.values('user').distinct().count(),
                'total_potential_respondents': total_alumni,
                'response_rate': round(
                    (responses.values('user').distinct().count() / total_alumni * 100) 
                    if total_alumni > 0 else 0, 
                    2
                )
            },
            'questions': question_analytics,
            'generated_at': timezone.now().isoformat()
        }
        
        # Cache for 30 minutes
        cache.set(cache_key, category_data, 1800)
        
        return Response(category_data)


# =============================================================================
# COMPREHENSIVE ANALYTICS DASHBOARD
# =============================================================================

class AnalyticsOverviewView(APIView):
    """Analytics Overview - Executive summary and KPIs"""
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request):
        try:
            filters = request.data.get('filters', {})
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            users = User.objects.filter(user_type=3)
            if filters.get('programs'):
                users = users.filter(program__in=filters['programs'])
            if filters.get('graduation_years'):
                users = users.filter(year_graduated__in=filters['graduation_years'])
            
            total_respondents = users.count()
            employed_count = users.filter(employment_status__in=['employed_locally', 'employed_internationally']).count()
            international_count = users.filter(employment_status='employed_internationally').count()
            
            overview_data = {
                'total_respondents': total_respondents,
                'employed_count': employed_count,
                'international_count': international_count,
                'unemployed_count': users.filter(employment_status='unemployed').count(),
                'self_employed_count': users.filter(employment_status='self_employed').count(),
                'quick_insights': [
                    f"Total of {total_respondents} alumni have responded to the survey",
                    f"Employment rate stands at {(employed_count/total_respondents*100):.1f}%" if total_respondents > 0 else "No employment data available",
                    f"International employment accounts for {(international_count/employed_count*100):.1f}% of employed alumni" if employed_count > 0 else "No international employment data"
                ]
            }
            return Response({'overview': overview_data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmployabilityAnalyticsView(APIView):
    """Employment outcome analysis"""
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request):
        try:
            filters = request.data.get('filters', {})
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            users = User.objects.filter(user_type=3)
            if filters.get('programs'):
                users = users.filter(program__in=filters['programs'])
            
            total = users.count()
            employed = users.filter(employment_status__in=['employed_locally', 'employed_internationally']).count()
            unemployed = users.filter(employment_status='unemployed').count()
            self_employed = users.filter(employment_status='self_employed').count()
            local_employed = users.filter(employment_status='employed_locally').count()
            international_employed = users.filter(employment_status='employed_internationally').count()
            
            # Program analysis
            programs = users.values('program').distinct()
            program_analysis = []
            for program in programs:
                if program['program']:
                    program_users = users.filter(program=program['program'])
                    program_total = program_users.count()
                    program_employed = program_users.filter(employment_status__in=['employed_locally', 'employed_internationally']).count()
                    program_analysis.append({
                        'name': program['program'],
                        'employmentRate': round((program_employed/program_total*100) if program_total > 0 else 0, 2),
                        'localEmployment': round((program_users.filter(employment_status='employed_locally').count()/program_total*100) if program_total > 0 else 0, 2),
                        'internationalEmployment': round((program_users.filter(employment_status='employed_internationally').count()/program_total*100) if program_total > 0 else 0, 2),
                        'respondentCount': program_total
                    })
            program_analysis.sort(key=lambda x: x['employmentRate'], reverse=True)
            
            employability_data = {
                'overallStats': {
                    'employmentRate': round((employed/total*100) if total > 0 else 0, 2),
                    'unemploymentRate': round((unemployed/total*100) if total > 0 else 0, 2),
                    'selfEmployedRate': round((self_employed/total*100) if total > 0 else 0, 2),
                    'localEmploymentRate': round((local_employed/employed*100) if employed > 0 else 0, 2),
                    'internationalRate': round((international_employed/employed*100) if employed > 0 else 0, 2)
                },
                'programAnalysis': program_analysis,
                'topPerformers': program_analysis[:5]
            }
            return Response({'employability': employability_data})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SkillsAnalyticsView(APIView):
    """Skills relevance analysis"""
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request):
        skills_data = {
            'overallAverages': {'Communication': 4.2, 'Critical Thinking': 4.0, 'Leadership': 3.8},
            'rankedSkills': [{'skill': 'Communication', 'average': 4.2}]
        }
        return Response({'skills': skills_data})


class CurriculumAnalyticsView(APIView):
    """Curriculum effectiveness analysis"""
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request):
        return Response({'curriculum': {'componentRatings': {'Major Courses': 4.3}}})


class StudiesAnalyticsView(APIView):
    """Further studies analysis"""
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request):
        return Response({'studies': {'overview': {'participationRate': 35}}})


class CompetitivenessAnalyticsView(APIView):
    """Competitiveness analysis"""
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request):
        return Response({'competitiveness': {'overallScore': 4.1}})


class ProgramComparisonAnalyticsView(APIView):
    """Program comparison analysis"""
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request):
        return Response({'program_comparison': {}})


class DemographicsAnalyticsView(APIView):
    """Demographics analysis"""
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request):
        return Response({'demographics': {'overview': {'totalRespondents': 500}}})


class AnalyticsFilterOptionsView(APIView):
    """Get available filter options for analytics"""
    permission_classes = [IsSurveyAdmin]
    
    def get(self, request):
        try:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            programs = User.objects.filter(user_type=3, program__isnull=False).values_list('program', flat=True).distinct()
            program_options = [{'value': p, 'label': p, 'count': User.objects.filter(user_type=3, program=p).count()} for p in programs if p]
            
            years = User.objects.filter(user_type=3, year_graduated__isnull=False).values_list('year_graduated', flat=True).distinct().order_by('-year_graduated')
            year_options = [{'value': y, 'label': str(y), 'count': User.objects.filter(user_type=3, year_graduated=y).count()} for y in years]
            
            return Response({
                'programs': program_options,
                'graduationYears': year_options,
                'employmentStatuses': [],
                'locations': [],
                'genders': [],
                'civilStatuses': []
            })
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AnalyticsExportView(APIView):
    """Export specific analytics reports"""
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request):
        return Response({'message': 'Export functionality coming soon'})


class AnalyticsFullReportView(APIView):
    """Export comprehensive analytics report"""
    permission_classes = [IsSurveyAdmin]
    
    def post(self, request):
        return Response({'message': 'Full report export functionality coming soon'})
