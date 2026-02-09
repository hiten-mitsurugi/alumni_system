"""
Connection Management Views - Follow/Unfollow, Invitations, Connection Status
"""
from .base_imports import *

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
        
        # Create notification for connection invitation
        from notifications_app.utils import create_notification
        create_notification(
            user=target_user,
            actor=request.user,
            notification_type='social',
            title='Connection Request',
            message=f"{request.user.first_name} {request.user.last_name} wants to connect with you",
            link_route='/alumni/connections',
            link_params={'tab': 'invitations'},
            metadata={'invitation_id': following.id}
        )
        
        return Response({
            'message': 'Connection request sent successfully',
            'status': 'pending'
        }, status=status.HTTP_201_CREATED)
    
    def delete(self, request, user_id):
        """Disconnect from a user (removes mutual connection)"""
        logger.info(f"Unfollow request: User {request.user.id} wants to unfollow User {user_id}")
        
        try:
            target_user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            logger.error(f"Target user {user_id} not found")
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
        
        try:
            from auth_app.models import Following
            
            # Check if the following relationship exists
            following = Following.objects.get(follower=request.user, following=target_user)
            logger.info(f"Found following relationship: {following.id} (status: {following.status})")
            
            # Remove the connection from current user to target user
            following.delete()
            logger.info(f"Deleted following relationship: {request.user.id} → {target_user.id}")
            
            # Remove the reverse connection (mutual disconnection)
            reverse_following = Following.objects.filter(
                follower=target_user, 
                following=request.user
            ).first()
            
            if reverse_following:
                reverse_following.delete()
                logger.info(f"Deleted reverse following relationship: {target_user.id} → {request.user.id}")
            else:
                logger.info("No reverse following relationship found")
            
            return Response({
                'message': 'Successfully disconnected from user',
                'unfollowed_user': {
                    'id': target_user.id,
                    'name': f"{target_user.first_name} {target_user.last_name}",
                    'email': target_user.email
                }
            }, status=status.HTTP_200_OK)
            
        except Following.DoesNotExist:
            logger.error(f"No following relationship found between {request.user.id} and {target_user.id}")
            return Response({'error': 'Not connected to this user'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Error unfollowing user: {str(e)}")
            return Response({'error': 'An error occurred while unfollowing user'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


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
        def serialize_following_relationship(following_obj, perspective='following'):
            """
            Serialize a Following relationship from a specific perspective
            perspective: 'following' = show the person being followed
                        'follower' = show the person who is following
            """
            if perspective == 'following':
                # Show the person you are following
                user_data = UserDetailSerializer(following_obj.following).data
            else:  # perspective == 'follower'
                # Show the person who is following you
                user_data = UserDetailSerializer(following_obj.follower).data
            
            return {
                'id': following_obj.id,
                'user': user_data,
                'status': following_obj.status,
                'created_at': following_obj.created_at,
                'is_mutual': getattr(following_obj, 'is_mutual', False)
            }
        
        if connection_type == 'followers':
            connections = Following.objects.filter(following=user, status='accepted').select_related('follower')
            data = [serialize_following_relationship(conn, 'follower') for conn in connections]
        elif connection_type == 'following':
            connections = Following.objects.filter(follower=user, status='accepted').select_related('following')
            data = [serialize_following_relationship(conn, 'following') for conn in connections]
        elif connection_type == 'mutual':
            connections = Following.objects.filter(
                following=user, is_mutual=True, status='accepted'
            ).select_related('follower')
            data = [serialize_following_relationship(conn, 'follower') for conn in connections]
        elif connection_type == 'invitations':
            # Get pending invitations sent TO the current user
            invitations = Following.objects.filter(
                following=user, status='pending'
            ).select_related('follower')
            data = [serialize_following_relationship(inv, 'follower') for inv in invitations]
            return Response(data)
        else:  # all
            followers = Following.objects.filter(following=user, status='accepted').select_related('follower')
            following = Following.objects.filter(follower=user, status='accepted').select_related('following')
            invitations = Following.objects.filter(following=user, status='pending').select_related('follower')
            
            # Debug: Log what invitations we're returning
            logger.info(f"User {user.id} invitations query: {[inv.id for inv in invitations]}")
            
            return Response({
                'followers': [serialize_following_relationship(conn, 'follower') for conn in followers],
                'following': [serialize_following_relationship(conn, 'following') for conn in following],
                'invitations': [serialize_following_relationship(inv, 'follower') for inv in invitations],
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
        logger.info(f"Accepting invitation {invitation_id} for user {request.user.id}")
        
        try:
            from auth_app.models import Following
            invitation = Following.objects.get(
                id=invitation_id,
                following=request.user,  # Invitation sent TO current user
                status='pending'
            )
            
            logger.info(f"Found invitation: {invitation.id} from user {invitation.follower.id} to user {invitation.following.id}")
            
            # Additional validation to prevent accepting own invitations
            if invitation.follower == request.user:
                logger.error(f"User {request.user.id} cannot accept their own invitation {invitation_id}")
                return Response({'error': 'Cannot accept your own invitation'}, status=status.HTTP_400_BAD_REQUEST)
            
            # Accept the invitation
            invitation.status = 'accepted'
            invitation.save()
            
            # Create notification for the person who sent the invitation
            from notifications_app.utils import create_notification
            create_notification(
                user=invitation.follower,  # Person who sent the invitation
                actor=request.user,        # Person who accepted
                notification_type='social',
                title='Connection Accepted',
                message=f"{request.user.first_name} {request.user.last_name} accepted your connection request",
                link_route='/alumni/profile',
                link_params={'userId': request.user.id},
                metadata={'connection_id': invitation.id}
            )
            
            logger.info(f"Successfully accepted invitation {invitation_id}")
            
            return Response({
                'message': f'Connection accepted with {invitation.follower.first_name} {invitation.follower.last_name}!',
                'status': 'accepted'
            }, status=status.HTTP_200_OK)
            
        except Following.DoesNotExist:
            logger.error(f"Invitation {invitation_id} not found for user {request.user.id}")
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


class TestConnectionStatusView(APIView):
    """Test endpoint to check connection status between users"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request, user_id):
        try:
            from auth_app.models import Following
            
            # Check if connection exists
            connection = Following.objects.filter(
                follower=request.user,
                following_id=user_id
            ).first()
            
            reverse_connection = Following.objects.filter(
                follower_id=user_id,
                following=request.user
            ).first()
            
            return Response({
                'current_user': request.user.id,
                'target_user': user_id,
                'connection_exists': connection is not None,
                'connection_status': connection.status if connection else None,
                'reverse_connection_exists': reverse_connection is not None,
                'reverse_connection_status': reverse_connection.status if reverse_connection else None,
                'is_mutual': connection.is_mutual if connection else False
            })
        except Exception as e:
            logger.error(f"Error checking connection status: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
