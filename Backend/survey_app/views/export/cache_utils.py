"""
Cache Management Utilities
===========================
Functions for clearing survey-related cache.
"""

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils import timezone

from ...permissions import IsSuperAdminOnly


@api_view(['POST'])
@permission_classes([IsSuperAdminOnly])
def clear_survey_cache_view(request):
    """
    Clear all survey-related cache.
    Super admin only utility endpoint.
    NOTE: Registration survey no longer uses caching.
    """
    return Response({
        'message': 'No cache clearing needed - registration survey fetches live data',
        'cleared_at': timezone.now().isoformat()
    })
