from rest_framework.permissions import BasePermission


class IsSurveyAdmin(BasePermission):
    """
    Permission class for survey administration.
    Only Super Admins (user_type=1) and Admins (user_type=2) can manage surveys.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.user_type in [1, 2]
        )


class IsSuperAdminOnly(BasePermission):
    """
    Permission class for super admin only actions.
    Only Super Admins (user_type=1) can perform certain critical actions.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.user_type == 1
        )


class IsAlumni(BasePermission):
    """
    Permission class for alumni users.
    Only Alumni (user_type=3) can respond to surveys.
    """
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and 
            request.user.user_type == 3
        )


class CanRespondToSurveys(BasePermission):
    """
    Permission class for survey responses.
    Authenticated users can respond to surveys, but only alumni should in practice.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated


class IsSurveyOwnerOrAdmin(BasePermission):
    """
    Permission class for survey ownership.
    Users can view/edit their own survey responses, admins can view all.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Admin users can access any survey data
        if request.user.user_type in [1, 2]:
            return True
        
        # Users can only access their own survey responses
        if hasattr(obj, 'user'):
            return obj.user == request.user
        
        # For questions/categories, anyone authenticated can view
        return True


class CanDistributeSurveys(BasePermission):
    """
    Permission class for survey distribution (Problem 1: Role Separation).
    Admins (user_type=2) and Super Admins (user_type=1) can view shareable surveys
    to distribute links via posts/messages, but only for read-only access.
    This allows survey visibility without granting management permissions.
    """
    def has_permission(self, request, view):
        # Only allow authenticated admins and super admins
        if not request.user.is_authenticated:
            return False
        
        # Allow both admin and super admin to view shareable surveys
        if request.user.user_type in [1, 2]:
            return True
        
        return False
