from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 2


class IsSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 1


class IsAlumni(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type == 3


class IsAdminOrSuperAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [1, 2]
