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


def get_survey_non_respondents(survey_template, filters=None):
    """
    Get list of approved alumni who have not responded to a specific survey.
    
    Args:
        survey_template (SurveyTemplate): The survey template to check responses for
        filters (dict, optional): Additional filters (program, year_graduated, etc.)
    
    Returns:
        QuerySet: Alumni users who haven't responded to this survey
        
    Logic:
        - Get all approved alumni (user_type=3, is_approved=True)
        - Exclude those who have submitted responses to this form
        - Apply optional filters (program, year_graduated, etc.)
    """
    from django.contrib.auth import get_user_model
    from survey_app.models import SurveyResponse
    
    User = get_user_model()
    
    # Get all approved alumni
    alumni = User.objects.filter(
        user_type=3,  # Alumni
        is_approved=True,
        is_active=True
    )
    
    # Get users who HAVE responded to this survey (form)
    responded_user_ids = SurveyResponse.objects.filter(
        form=survey_template
    ).values_list('user_id', flat=True).distinct()
    
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


def get_survey_response_statistics(survey_template):
    """
    Get response statistics for a survey.
    
    Args:
        survey_template (SurveyTemplate): The survey template to analyze
    
    Returns:
        dict: Statistics about survey responses
            - total_alumni: Total approved alumni count
            - total_respondents: Count of alumni who responded
            - total_non_respondents: Count of alumni who haven't responded
            - response_rate: Percentage of alumni who responded
    """
    from django.contrib.auth import get_user_model
    from survey_app.models import SurveyResponse
    
    User = get_user_model()
    
    # Total approved alumni
    total_alumni = User.objects.filter(
        user_type=3,
        is_approved=True,
        is_active=True
    ).count()
    
    # Get unique respondents for this form
    total_respondents = SurveyResponse.objects.filter(
        form=survey_template
    ).values('user_id').distinct().count()
    
    # Calculate non-respondents
    total_non_respondents = total_alumni - total_respondents
    
    # Calculate response rate
    response_rate = (total_respondents / total_alumni * 100) if total_alumni > 0 else 0
    
    return {
        'total_alumni': total_alumni,
        'total_respondents': total_respondents,
        'total_non_respondents': total_non_respondents,
        'response_rate': round(response_rate, 2)
    }
