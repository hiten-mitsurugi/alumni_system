from .base import *


class ApprovedAlumniListView(ListAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminOrSuperAdmin]

    def get_queryset(self):
        request = self.request
        employment_status = request.query_params.get('employment_status', '').strip().lower()
        gender = request.query_params.get('gender', '').strip().lower()
        year_graduated = request.query_params.get('year_graduated', '').strip()
        program = request.query_params.get('program', '').strip()
        status = request.query_params.get('status', '').strip().lower()
        search = request.query_params.get('search', '').strip()
        
        # Temporarily disable caching to debug approved users issue
        # cache_key = f"approved_alumni_list_{employment_status}_{gender}_{year_graduated}_{program}_{status}_{search}"
        # cached_ids = cache.get(cache_key)
        # if cached_ids is not None:
        #     return CustomUser.objects.filter(id__in=cached_ids)
            
        queryset = CustomUser.objects.filter(user_type=3, is_approved=True)
        
        # Log the base queryset for debugging
        logger.info(f"ApprovedAlumniListView: Base queryset count: {queryset.count()}")
        for user in queryset[:5]:  # Log first 5 users
            logger.info(f"Approved user: {user.id} - {user.email} - {user.first_name} {user.last_name}")
        
        if employment_status:
            queryset = queryset.filter(employment_status__iexact=employment_status)
        if gender:
            queryset = queryset.filter(sex__iexact=gender)
        if year_graduated:
            queryset = queryset.filter(year_graduated=year_graduated)
        if program:
            queryset = queryset.filter(program=program)
        if status:
            if status == 'active':
                queryset = queryset.filter(is_active=True)
            elif status == 'blocked':
                queryset = queryset.filter(is_active=False)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search)
            )
        
        logger.info(f"ApprovedAlumniListView: Final queryset count after filters: {queryset.count()}")
        
        # Re-enable caching later after fixing the issue
        # user_ids = list(queryset.values_list('id', flat=True))
        # cache.set(cache_key, user_ids, timeout=3600)
        return queryset


class PendingAlumniListView(ListAPIView):
    serializer_class = UserDetailSerializer
    permission_classes = [IsAdminOrSuperAdmin]
    pagination_class = None 

    def get_queryset(self):
        return CustomUser.objects.filter(user_type=3, is_approved=False)


class UserDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cache_key = f'user_detail_{request.user.id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)
        serializer = UserDetailSerializer(request.user)
        cache.set(cache_key, serializer.data, timeout=3600)
        return Response(serializer.data)


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSearchSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CustomUser.objects.all()
        search_query = self.request.query_params.get('q', None)
        if search_query:
            queryset = queryset.filter(
                Q(first_name__icontains=search_query) |
                Q(last_name__icontains=search_query) |
                Q(username__icontains=search_query)
            ).exclude(id=self.request.user.id)
        return queryset

    def get_permissions(self):
        """
        Instantiates and returns the list of permissions that this view requires.
        Only allow admins and super admins to delete users.
        """
        if self.action == 'destroy':
            # Custom permission check for delete - must be Admin or SuperAdmin
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def destroy(self, request, *args, **kwargs):
        """
        Custom delete method for user deletion with additional checks
        """
        instance = self.get_object()
        
        # Check if user has permission to delete (Admin=2 or SuperAdmin=1)
        if request.user.user_type not in [1, 2]:
            return Response(
                {"error": "You don't have permission to delete users"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Prevent users from deleting themselves
        if instance == request.user:
            return Response(
                {"error": "You cannot delete your own account"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prevent deletion of super admin by regular admin
        # user_type: 1=Super Admin, 2=Admin, 3=Alumni
        if instance.user_type == 1 and request.user.user_type != 1:
            return Response(
                {"error": "Only super admins can delete other super admin accounts"}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Clear any cached data related to this user
        cache_keys_to_clear = [
            f"user_approval_count",
            f"pending_users_list",
            f"approved_users_list",
            f"user_status_{instance.id}",
            f"user_profile_{instance.id}",
        ]
        
        for key in cache_keys_to_clear:
            cache.delete(key)
        
        # Also clear pattern-based cache keys
        cache_patterns = [
            "user_*",
            "approval_*",
            "pending_*",
            "approved_*"
        ]
        
        for pattern in cache_patterns:
            cache_keys = cache.keys(pattern)
            if cache_keys:
                cache.delete_many(cache_keys)
        
        # Broadcast the user deletion to WebSocket
        channel_layer = get_channel_layer()
        if channel_layer:
            try:
                async_to_sync(channel_layer.group_send)(
                    "admin_notifications",
                    {
                        "type": "user_deleted",
                        "user_id": instance.id,
                        "user_name": f"{instance.first_name} {instance.last_name}",
                        "deleted_by": f"{request.user.first_name} {request.user.last_name}"
                    }
                )
            except Exception as e:
                print(f"Error broadcasting user deletion: {e}")
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)