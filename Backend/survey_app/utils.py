"""
Survey App Utilities
====================
Helper functions for survey management, including slug generation for shareable surveys.
"""

import uuid
from django.utils.text import slugify


def generate_unique_survey_slug(survey_name, max_length=50):
    """
    Generate a unique, URL-safe slug for a survey.
    
    Args:
        survey_name (str): The name of the survey
        max_length (int): Maximum length for the slug (default: 50)
    
    Returns:
        str: A unique slug combining sanitized name and UUID
        
    Example:
        "Alumni Employment Survey" -> "alumni-employment-survey-a1b2c3d4"
    """
    # Create base slug from survey name
    base_slug = slugify(survey_name)[:max_length-9]  # Reserve 9 chars for UUID
    
    # Add short UUID to ensure uniqueness
    unique_id = str(uuid.uuid4())[:8]
    
    # Combine for final slug
    unique_slug = f"{base_slug}-{unique_id}"
    
    return unique_slug


def get_survey_public_url(survey_slug, request=None):
    """
    Generate the full public URL for a shareable survey.
    
    Args:
        survey_slug (str): The public slug of the survey
        request (HttpRequest, optional): Django request object to extract domain
    
    Returns:
        str: Full URL to access the survey
        
    Example:
        "alumni-employment-survey-a1b2c3d4" -> 
        "https://alumni.system.com/survey/alumni-employment-survey-a1b2c3d4"
    """
    if request:
        # Use request to build absolute URL
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        return f"{protocol}://{host}/survey/{survey_slug}"
    else:
        # Return relative path (frontend will handle base URL)
        return f"/survey/{survey_slug}"


def validate_survey_sharing_eligibility(survey):
    """
    Check if a survey is eligible for sharing.
    
    Args:
        survey (SurveyTemplate): The survey template to validate
    
    Returns:
        tuple: (bool, str) - (is_eligible, reason_if_not)
        
    Validation Rules:
        - Survey must be published
        - Survey must be active
        - Survey must be accepting responses
        - Survey must not be expired (if end_at is set)
    """
    from django.utils import timezone
    
    if not survey.is_published:
        return False, "Survey must be published before sharing"
    
    if not survey.is_active:
        return False, "Survey must be active"
    
    if not survey.accepting_responses:
        return False, "Survey must be accepting responses"
    
    # Check if survey has expired
    if survey.end_at and timezone.now() >= survey.end_at:
        return False, "Survey has expired"
    
    # Check if survey hasn't started yet
    if survey.start_at and timezone.now() < survey.start_at:
        return False, "Survey has not started yet"
    
    return True, "Survey is eligible for sharing"


def get_survey_non_respondents(survey_template, filters=None, min_completion_rate=0.5):
    """
    Get list of approved alumni who have not responded to a specific survey.
    
    Args:
        survey_template (SurveyTemplate): The survey template to check responses for
        filters (dict, optional): Additional filters (program, year_graduated, etc.)
        min_completion_rate (float): Minimum completion rate (0.0-1.0) to be considered a respondent (default: 0.5 = 50%)
    
    Returns:
        QuerySet: Alumni users who haven't responded to this survey or didn't meet completion threshold
        
    Logic:
        - Get all approved alumni (user_type=3, is_approved=True)
        - Exclude those who have submitted responses to questions in this survey's categories
        - Only count as "responded" if they answered >= min_completion_rate of questions
        - Apply optional filters (program, year_graduated, etc.)
    """
    from django.contrib.auth import get_user_model
    from survey_app.models import SurveyResponse, SurveyQuestion, SurveyTemplateCategory
    from django.db.models import Count
    
    User = get_user_model()
    
    # Get all approved alumni
    alumni = User.objects.filter(
        user_type=3,  # Alumni
        is_approved=True,
        is_active=True
    )
    
    # Get categories for this survey template
    template_categories = SurveyTemplateCategory.objects.filter(template=survey_template)
    category_ids = template_categories.values_list('category_id', flat=True)
    
    # Get questions in those categories
    questions_in_survey = SurveyQuestion.objects.filter(
        category_id__in=category_ids,
        is_active=True
    )
    
    total_questions = questions_in_survey.count()
    min_answers_required = int(total_questions * min_completion_rate)
    
    # Get users who HAVE responded meaningfully to this survey
    # (must have answered at least min_completion_rate of questions)
    responded_user_ids = []
    
    all_responses = SurveyResponse.objects.filter(question__in=questions_in_survey)
    user_response_counts = all_responses.values('user_id').annotate(
        answer_count=Count('id')
    )
    
    for user_data in user_response_counts:
        if user_data['answer_count'] >= min_answers_required:
            responded_user_ids.append(user_data['user_id'])
    
    # Exclude respondents to get non-respondents
    non_respondents = alumni.exclude(id__in=responded_user_ids)
    
    # Apply optional filters
    if filters:
        if filters.get('program'):
            non_respondents = non_respondents.filter(program__icontains=filters['program'])
        
        if filters.get('year_graduated'):
            non_respondents = non_respondents.filter(year_graduated=filters['year_graduated'])
        
        if filters.get('year_graduated_from'):
            non_respondents = non_respondents.filter(year_graduated__gte=filters['year_graduated_from'])
        
        if filters.get('year_graduated_to'):
            non_respondents = non_respondents.filter(year_graduated__lte=filters['year_graduated_to'])
    
    # Order by most recently active first
    non_respondents = non_respondents.order_by('-last_login', 'last_name', 'first_name')
    
    return non_respondents


def get_survey_response_statistics(survey_template, programs=None, graduation_years=None, min_completion_rate=0.5):
    """
    Get response statistics for a survey.
    
    Args:
        survey_template (SurveyTemplate): The survey template to analyze
        programs (list, optional): Filter by specific programs
        graduation_years (list, optional): Filter by specific graduation years
        min_completion_rate (float): Minimum completion rate (0.0-1.0) to be considered a respondent (default: 0.5 = 50%)
    
    Returns:
        dict: Statistics about survey responses
            - total_alumni: Total approved alumni count (filtered)
            - total_respondents: Count of alumni who responded with min completion rate
            - total_non_respondents: Count of alumni who haven't responded or didn't meet completion threshold
            - response_rate: Percentage of alumni who responded
            - partial_respondents: Count of users who started but didn't meet completion threshold
    """
    from django.contrib.auth import get_user_model
    from survey_app.models import SurveyResponse, SurveyQuestion, SurveyTemplateCategory
    from django.db.models import Count, Q
    
    User = get_user_model()
    
    # Start with all approved alumni
    alumni_query = User.objects.filter(
        user_type=3,
        is_approved=True,
        is_active=True
    )
    
    # Apply program filter
    if programs and len(programs) > 0:
        program_filter = Q()
        for program in programs:
            program_filter |= Q(program__icontains=program)
        alumni_query = alumni_query.filter(program_filter)
    
    # Apply graduation year filter
    if graduation_years and len(graduation_years) > 0:
        alumni_query = alumni_query.filter(year_graduated__in=graduation_years)
    
    # Total approved alumni (after filters)
    total_alumni = alumni_query.count()
    
    # Get categories for this survey template
    template_categories = SurveyTemplateCategory.objects.filter(template=survey_template)
    category_ids = template_categories.values_list('category_id', flat=True)
    
    # Get questions in those categories
    questions_in_survey = SurveyQuestion.objects.filter(
        category_id__in=category_ids,
        is_active=True
    )
    
    total_questions = questions_in_survey.count()
    min_answers_required = int(total_questions * min_completion_rate)
    
    # Get respondents who met the minimum completion threshold
    # Only count responses from filtered alumni
    filtered_alumni_ids = alumni_query.values_list('id', flat=True)
    
    all_responses = SurveyResponse.objects.filter(
        question__in=questions_in_survey,
        user_id__in=filtered_alumni_ids
    )
    
    user_response_counts = all_responses.values('user_id').annotate(
        answer_count=Count('id')
    )
    
    total_respondents = 0
    partial_respondents = 0
    
    for user_data in user_response_counts:
        if user_data['answer_count'] >= min_answers_required:
            total_respondents += 1
        else:
            partial_respondents += 1
    
    # Calculate non-respondents
    total_non_respondents = total_alumni - total_respondents
    
    # Calculate response rate
    response_rate = (total_respondents / total_alumni * 100) if total_alumni > 0 else 0
    
    return {
        'total_alumni': total_alumni,
        'total_respondents': total_respondents,
        'total_non_respondents': total_non_respondents,
        'response_rate': round(response_rate, 2),
        'partial_respondents': partial_respondents,
        'total_questions': total_questions,
        'min_answers_required': min_answers_required
    }
