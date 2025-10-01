from .base import *


class SuggestedConnectionsView(APIView):
    """Get suggested connections for user"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get users from same program/year who user isn't following
        try:
            if Follow:
                following_ids = Follow.objects.filter(follower=user).values_list('following_id', flat=True)
                suggestions = CustomUser.objects.filter(
                    user_type=3,  # Alumni
                    is_approved=True,
                    program=user.program,
                    year_graduated=user.year_graduated
                ).exclude(
                    id__in=list(following_ids) + [user.id]
                )[:10]
            else:
                # Fallback if Follow model doesn't exist
                suggestions = CustomUser.objects.filter(
                    user_type=3,
                    is_approved=True,
                    program=user.program,
                    year_graduated=user.year_graduated
                ).exclude(id=user.id)[:10]
        except:
            suggestions = CustomUser.objects.none()
        
        from ..serializers import UserDetailSerializer
        serializer = UserDetailSerializer(suggestions, many=True, context={'request': request})
        return Response(serializer.data)


class UserByNameView(APIView):
    """Get user by username for URL routing"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_name):
        try:
            user = CustomUser.objects.get(username=user_name, is_approved=True)
            from ..serializers import UserDetailSerializer
            serializer = UserDetailSerializer(user, context={'request': request})
            return Response(serializer.data)
        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


class InvitationAcceptView(APIView):
    """Accept invitation"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, invitation_id):
        # This would handle invitation acceptance if invitation system exists
        try:
            from ..models import Invitation
            invitation = Invitation.objects.get(id=invitation_id, recipient=request.user)
            invitation.status = 'accepted'
            invitation.save()
            
            # Create follow relationship if it's a connection invitation
            if Follow and invitation.invitation_type == 'connection':
                Follow.objects.get_or_create(
                    follower=invitation.recipient,
                    following=invitation.sender
                )
            
            return Response({'status': 'accepted'})
        except ImportError:
            return Response({'error': 'Invitation system not available'}, 
                          status=status.HTTP_501_NOT_IMPLEMENTED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class InvitationRejectView(APIView):
    """Reject invitation"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request, invitation_id):
        try:
            from ..models import Invitation
            invitation = Invitation.objects.get(id=invitation_id, recipient=request.user)
            invitation.status = 'rejected'
            invitation.save()
            return Response({'status': 'rejected'})
        except ImportError:
            return Response({'error': 'Invitation system not available'}, 
                          status=status.HTTP_501_NOT_IMPLEMENTED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class TestStatusBroadcastView(APIView):
    """Test status broadcast functionality"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            # Test broadcasting user status
            channel_layer = get_channel_layer()
            if channel_layer:
                async_to_sync(channel_layer.group_send)(
                    f"user_{request.user.id}",
                    {
                        "type": "status_update",
                        "message": "Test broadcast successful"
                    }
                )
                return Response({'message': 'Broadcast sent successfully'})
            else:
                return Response({'error': 'Channel layer not available'})
        except Exception as e:
            return Response({'error': f'Broadcast failed: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DebugUsersView(APIView):
    """Debug view for user information"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def get(self, request):
        users_data = []
        users = CustomUser.objects.all()[:10]  # Limit to 10 for debugging
        
        for user in users:
            user_info = {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'user_type': user.user_type,
                'is_approved': user.is_approved,
                'is_active': user.is_active,
                'last_login': user.last_login,
                'date_joined': user.date_joined,
            }
            
            # Add profile info if exists
            if hasattr(user, 'profile') and user.profile:
                user_info['profile'] = {
                    'bio': user.profile.bio,
                    'location': user.profile.location,
                    'profile_picture': str(user.profile.profile_picture) if user.profile.profile_picture else None
                }
            
            users_data.append(user_info)
        
        return Response({
            'total_users': CustomUser.objects.count(),
            'users_sample': users_data
        })


class ClearCacheView(APIView):
    """Clear cache for testing purposes"""
    permission_classes = [IsAuthenticated, IsAdminUser]
    
    def post(self, request):
        try:
            cache.clear()
            return Response({'message': 'Cache cleared successfully'})
        except Exception as e:
            return Response({'error': f'Failed to clear cache: {str(e)}'}, 
                          status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CheckEmailExistsView(APIView):
    """Check if email already exists"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, 
                          status=status.HTTP_400_BAD_REQUEST)
        
        exists = CustomUser.objects.filter(email=email).exists()
        return Response({'exists': exists})