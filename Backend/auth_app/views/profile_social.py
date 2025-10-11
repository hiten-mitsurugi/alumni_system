"""
Profile and Social Views - LinkedIn-style profile features, connections, invitations
"""
from .base_imports import *

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
        from auth_app.models import Profile
        profile, created = Profile.objects.get_or_create(user=user)
        
        # Use basic serializer since EnhancedUserDetailSerializer might not exist
        serializer = UserDetailSerializer(user, context={'request': request})
        return Response(serializer.data)

    def patch(self, request):
        """Update current user's profile"""
        user = request.user
        from auth_app.models import Profile
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
        
        # Handle profile picture upload (store on user model) - save with unique filename
        if 'profile_picture' in request.FILES:
            try:
                pic = request.FILES['profile_picture']
                # Ensure extension preserved
                ext = os.path.splitext(pic.name)[1] or ''
                new_name = f"profile_{user.id}_{uuid.uuid4().hex}{ext}"
                # Save directly to user.profile_picture field
                user.profile_picture.save(new_name, pic, save=True)
                user.save()
                # Log upload
                logger.info(f"Saved new profile picture for user {user.id}: {user.profile_picture.name}")
            except Exception as e:
                logger.error(f"Failed to save profile picture for user {user.id}: {str(e)}")

        # Handle cover photo upload
        if 'cover_photo' in request.FILES:
            profile_data['cover_photo'] = request.FILES['cover_photo']
        
        # Update profile
        for field, value in profile_data.items():
            if hasattr(profile, field):
                setattr(profile, field, value)
        profile.save()

        # Clear cache keys related to this user so updated URLs are returned
        cache.delete(f"user_profile_{user.id}")
        cache.delete(f"user_detail_{user.id}")
        cache.delete("approved_alumni_list")

        # Return updated profile
        serializer = UserDetailSerializer(user, context={'request': request})
        return Response(serializer.data)


class FollowUserView(APIView):
    """Follow/Unfollow a user"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, user_id):
        """Send connection invitation to a user (LinkedIn-style)"""
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        if target_user == request.user:
            return Response({'error': 'Cannot connect to yourself'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Import here to avoid circular imports
        from auth_app.models import Following
        
        # Check if already connected or has pending request
        existing_connection = Following.objects.filter(
            follower=request.user,
            following=target_user
        ).first()
        
        if existing_connection:
            if existing_connection.status == 'pending':
                return Response({'message': 'Connection request already sent'}, status=status.HTTP_200_OK)
            elif existing_connection.status == 'accepted':
                return Response({'message': 'Already connected to this user'}, status=status.HTTP_200_OK)
        
        # Create pending connection request (LinkedIn-style)
        following = Following.objects.create(
            follower=request.user,
            following=target_user,
            status='pending'
        )
        
        return Response({
            'message': 'Connection request sent successfully',
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)
    
    def delete(self, request, user_id):
        """Disconnect from a user (removes mutual connection)"""
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            from auth_app.models import Following
            # Remove the connection from current user to target user
            following = Following.objects.get(follower=request.user, following=target_user)
            following.delete()
            
            # Remove the reverse connection (mutual disconnection)
            reverse_following = Following.objects.filter(
                follower=target_user, 
                following=request.user
            ).first()
            if reverse_following:
                reverse_following.delete()
            
            return Response({'message': 'Successfully disconnected from user'}, status=status.HTTP_200_OK)
        except Following.DoesNotExist:
            return Response({'error': 'Not connected to this user'}, status=status.HTTP_400_BAD_REQUEST)


class UserConnectionsView(APIView):
    """Get user's connections (followers/following)"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id=None):
        # If user_id is provided, get that user's connections; otherwise get current user's connections
        if user_id:
            try:
                user = CustomUser.objects.get(id=user_id)
            except CustomUser.DoesNotExist:
                return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            user = request.user
        
        connection_type = request.query_params.get('type', 'all')  # 'followers', 'following', 'mutual', 'all', 'invitations'
        
        from auth_app.models import Following
        
        # Create a simple serializer for Following relationships
        def serialize_following(following_obj):
            return {
                'id': following_obj.id,
                'user': UserDetailSerializer(following_obj.follower if hasattr(following_obj, 'follower') else following_obj.following).data,
                'status': following_obj.status,
                'created_at': following_obj.created_at,
                'is_mutual': getattr(following_obj, 'is_mutual', False)
            }
        
        if connection_type == 'followers':
            connections = Following.objects.filter(following=user, status='accepted').select_related('follower')
            data = [serialize_following(conn) for conn in connections]
        elif connection_type == 'following':
            connections = Following.objects.filter(follower=user, status='accepted').select_related('following')
            data = [serialize_following(conn) for conn in connections]
        elif connection_type == 'mutual':
            connections = Following.objects.filter(
                following=user, is_mutual=True, status='accepted'
            ).select_related('follower')
            data = [serialize_following(conn) for conn in connections]
        elif connection_type == 'invitations':
            # Get pending invitations sent TO the current user
            invitations = Following.objects.filter(
                following=user, status='pending'
            ).select_related('follower')
            data = [serialize_following(inv) for inv in invitations]
            return Response(data)
        else:  # all
            followers = Following.objects.filter(following=user, status='accepted').select_related('follower')
            following = Following.objects.filter(follower=user, status='accepted').select_related('following')
            invitations = Following.objects.filter(following=user, status='pending').select_related('follower')
            
            return Response({
                'followers': [serialize_following(conn) for conn in followers],
                'following': [serialize_following(conn) for conn in following],
                'invitations': [serialize_following(inv) for inv in invitations],
                'followers_count': followers.count(),
                'following_count': following.count(),
                'mutual_count': Following.objects.filter(following=user, is_mutual=True, status='accepted').count(),
                'invitations_count': invitations.count()
            })
        
        return Response(data)


class InvitationManageView(APIView):
    """Accept or reject connection invitations"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, invitation_id):
        """Accept a connection invitation"""
        try:
            from auth_app.models import Following
            invitation = Following.objects.get(
                id=invitation_id,
                following=request.user,  # Invitation sent TO current user
                status='pending'
            )
            
            # Accept the invitation
            invitation.status = 'accepted'
            invitation.save()
            
            return Response({
                'message': f'Connection accepted with {invitation.follower.first_name} {invitation.follower.last_name}!',
                'status': 'accepted'
            }, status=status.HTTP_200_OK)
            
        except Following.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error accepting invitation {invitation_id}: {str(e)}")
            return Response({'error': 'Failed to accept invitation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, invitation_id):
        """Reject/ignore a connection invitation"""
        try:
            from auth_app.models import Following
            invitation = Following.objects.get(
                id=invitation_id,
                following=request.user,  # Invitation sent TO current user
                status='pending'
            )
            
            # Delete the invitation (reject it)
            sender_name = f"{invitation.follower.first_name} {invitation.follower.last_name}"
            invitation.delete()
            
            return Response({
                'message': f'Connection request from {sender_name} has been ignored.',
                'status': 'rejected'
            }, status=status.HTTP_200_OK)
            
        except Following.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error rejecting invitation {invitation_id}: {str(e)}")
            return Response({'error': 'Failed to reject invitation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvitationAcceptView(APIView):
    """Accept connection invitations"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, invitation_id):
        """Accept a connection invitation"""
        try:
            from auth_app.models import Following
            invitation = Following.objects.get(
                id=invitation_id,
                following=request.user,  # Invitation sent TO current user
                status='pending'
            )
            
            # Accept the invitation
            invitation.status = 'accepted'
            invitation.save()
            
            return Response({
                'message': f'Connection accepted with {invitation.follower.first_name} {invitation.follower.last_name}!',
                'status': 'accepted'
            }, status=status.HTTP_200_OK)
            
        except Following.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error accepting invitation {invitation_id}: {str(e)}")
            return Response({'error': 'Failed to accept invitation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class InvitationRejectView(APIView):
    """Reject connection invitations"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, invitation_id):
        """Reject/ignore a connection invitation"""
        try:
            from auth_app.models import Following
            invitation = Following.objects.get(
                id=invitation_id,
                following=request.user,  # Invitation sent TO current user
                status='pending'
            )
            
            # Delete the invitation (reject it)
            sender_name = f"{invitation.follower.first_name} {invitation.follower.last_name}"
            invitation.delete()
            
            return Response({
                'message': f'Connection request from {sender_name} has been ignored.',
                'status': 'rejected'
            }, status=status.HTTP_200_OK)
            
        except Following.DoesNotExist:
            return Response({'error': 'Invitation not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error rejecting invitation {invitation_id}: {str(e)}")
            return Response({'error': 'Failed to reject invitation'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProfileSearchView(APIView):
    """Search for alumni profiles"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        query = request.query_params.get('q', '')
        program = request.query_params.get('program', '')
        year_graduated = request.query_params.get('year_graduated', '')
        employment_status = request.query_params.get('employment_status', '')
        location = request.query_params.get('location', '')
        
        # Start with approved alumni
        queryset = CustomUser.objects.filter(user_type=3, is_approved=True, is_active=True)
        
        # Apply search filters
        if query:
            queryset = queryset.filter(
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query) |
                Q(email__icontains=query) |
                Q(username__icontains=query)
            )
        
        if program:
            queryset = queryset.filter(program__icontains=program)
            
        if year_graduated:
            queryset = queryset.filter(year_graduated=year_graduated)
            
        if employment_status:
            queryset = queryset.filter(employment_status__iexact=employment_status)
            
        if location:
            queryset = queryset.filter(
                Q(address__city__icontains=location) |
                Q(address__province__icontains=location) |
                Q(address__country__icontains=location)
            )
        
        # Limit results to prevent performance issues
        queryset = queryset[:50]
        
        serializer = UserSearchSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)


class SuggestedConnectionsView(APIView):
    """Get suggested connections for the user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get users the current user is not already connected to
        from auth_app.models import Following
        connected_user_ids = Following.objects.filter(
            Q(follower=user) | Q(following=user)
        ).values_list('follower_id', 'following_id')
        
        # Flatten the list and exclude current user
        exclude_ids = set()
        for follower_id, following_id in connected_user_ids:
            exclude_ids.add(follower_id)
            exclude_ids.add(following_id)
        exclude_ids.add(user.id)
        
        # Suggest alumni from same program or year
        suggestions = CustomUser.objects.filter(
            user_type=3, 
            is_approved=True, 
            is_active=True
        ).exclude(id__in=exclude_ids)
        
        # Prioritize by same program and year
        if user.program:
            suggestions = suggestions.filter(program=user.program)
        if user.year_graduated:
            suggestions = suggestions.filter(year_graduated=user.year_graduated)
        
        # Limit suggestions
        suggestions = suggestions[:10]
        
        serializer = UserSearchSerializer(suggestions, many=True, context={'request': request})
        return Response(serializer.data)


class UserByNameView(APIView):
    """Get user by username for URL routing"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_name):
        try:
            user = CustomUser.objects.get(
                username=user_name, 
                is_approved=True, 
                is_active=True
            )
            serializer = UserDetailSerializer(user, context={'request': request})
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
