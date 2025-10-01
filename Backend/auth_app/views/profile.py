from .base import *


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cache_key = f"user_profile_{user.id}"
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        serializer = ProfileSerializer(user)
        data = serializer.data
        cache.set(cache_key, data, timeout=300)
        return Response(data)

    def put(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache_key = f"user_profile_{user.id}"
            cache.set(cache_key, serializer.data, timeout=300)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request):
        user = request.user
        serializer = ProfileSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            cache_key = f"user_profile_{user.id}"
            cache.set(cache_key, serializer.data, timeout=300)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EnhancedProfileView(APIView):
    """Enhanced Profile view with LinkedIn-style features"""
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id=None, username=None):
        # Handle different lookup methods
        if username:
            # Lookup by username
            try:
                user = CustomUser.objects.get(username=username, is_approved=True, is_active=True)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        elif user_id:
            # Lookup by ID (legacy support)
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            # Current user's profile
            user = request.user

        # Get or create profile
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Use enhanced serializer with social features
        from ..serializers import EnhancedUserDetailSerializer
        serializer = EnhancedUserDetailSerializer(user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        """Update current user's profile"""
        user = request.user
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Update profile fields
        profile_data = {}
        updatable_fields = [
            'bio', 'headline', 'location', 'summary', 'linkedin_url', 'facebook_url', 
            'twitter_url', 'instagram_url', 'website_url', 'profile_visibility', 
            'allow_contact', 'allow_messaging'
        ]
        
        for field in updatable_fields:
            if field in request.data:
                profile_data[field] = request.data[field]
        
        # Handle cover photo upload
        if 'cover_photo' in request.FILES:
            profile_data['cover_photo'] = request.FILES['cover_photo']
        
        # Update profile
        for field, value in profile_data.items():
            setattr(profile, field, value)
        profile.save()
        
        # Clear cache
        cache_key = f"user_profile_{user.id}"
        cache.delete(cache_key)
        
        # Return updated profile
        from ..serializers import EnhancedUserDetailSerializer
        serializer = EnhancedUserDetailSerializer(user, context={'request': request})
        return Response(serializer.data)


class ProfileSearchView(APIView):
    """Search for alumni profiles"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        program = request.query_params.get('program', '')
        year_graduated = request.query_params.get('year_graduated', '')
        employment_status = request.query_params.get('employment_status', '')
        location = request.query_params.get('location', '')
        
        # Base queryset - only approved alumni
        queryset = CustomUser.objects.filter(
            user_type=3,  # Alumni only
            is_approved=True
        ).select_related('profile')
        
        # Apply filters
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(profile__headline__icontains=query) |
                Q(profile__summary__icontains=query) |
                Q(profile__present_occupation__icontains=query) |
                Q(profile__employing_agency__icontains=query)
            )
        
        if program:
            queryset = queryset.filter(program__icontains=program)
        
        if year_graduated:
            queryset = queryset.filter(year_graduated=year_graduated)
        
        if employment_status:
            queryset = queryset.filter(employment_status=employment_status)
        
        if location:
            queryset = queryset.filter(profile__location__icontains=location)
        
        # Exclude current user
        queryset = queryset.exclude(id=request.user.id)
        
        # Paginate results
        from rest_framework.pagination import PageNumberPagination
        paginator = PageNumberPagination()
        paginator.page_size = 20
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        from ..serializers import EnhancedUserDetailSerializer
        serializer = EnhancedUserDetailSerializer(
            paginated_queryset, 
            many=True, 
            context={'request': request}
        )
        
        return paginator.get_paginated_response(serializer.data)