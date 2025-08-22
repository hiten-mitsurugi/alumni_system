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
