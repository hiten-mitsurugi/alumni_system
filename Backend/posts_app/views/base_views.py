"""
Base classes for posts_app views.

This module contains shared permission and pagination classes used across the posts application.
"""

from rest_framework.pagination import PageNumberPagination


class IsAdminOrSuperAdmin:
    """Permission class for admin/superadmin users"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [1, 2]


class PostPagination(PageNumberPagination):
    """Custom pagination for posts"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
