class IsAdminOrSuperAdmin:
    """Permission class for admin/superadmin users"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [1, 2]