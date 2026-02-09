"""
Search views for users, groups, and messages in the messaging app.
Handles global search, user search, and conversation-level message search.
"""
import logging
from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from ..models import GroupChat, Message, BlockedUser
from ..serializers import UserSearchSerializer, GroupChatSerializer

User = get_user_model()
logger = logging.getLogger(__name__)


class SearchView(APIView):
    """Global search for users and groups"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        logger.info(f"🔍 Search request from user {request.user.id} for query: '{query}'")
        
        if not query:
            return Response({"users": [], "groups": []}, status=status.HTTP_200_OK)

        try:
            # Get blocked users to mark them as blocked (but still show them in search)
            blocked_user_ids = BlockedUser.objects.filter(user=request.user).values_list('blocked_user_id', flat=True)
            blocked_by_user_ids = BlockedUser.objects.filter(blocked_user=request.user).values_list('user_id', flat=True)

            # ✅ Search users (show all users, don't exclude blocked ones)
            users_qs = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).exclude(
                id=request.user.id  # Only exclude self
            )

            # ✅ Apply filters - ensure these attributes exist
            users_qs = users_qs.filter(is_approved=True, user_type=3, is_active=True)
            users = users_qs.distinct()

            # ✅ Search groups
            groups = GroupChat.objects.filter(name__icontains=query)

            logger.info(f"🔍 Found {users.count()} users and {groups.count()} groups for query: '{query}'")

            # ✅ Serialize with error handling
            try:
                user_serializer = UserSearchSerializer(users, many=True, context={"request": request})
                user_data = user_serializer.data
            except Exception as e:
                logger.error(f"🔍 User serialization error: {str(e)}")
                user_data = []

            try:
                group_serializer = GroupChatSerializer(groups, many=True)
                group_data = group_serializer.data
            except Exception as e:
                logger.error(f"🔍 Group serialization error: {str(e)}")
                group_data = []

            response_data = {
                "users": user_data,
                "groups": group_data
            }
            
            logger.info(f"🔍 Returning {len(user_data)} users and {len(group_data)} groups")
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"🔍 Search error for query '{query}': {str(e)}")
            return Response({
                "users": [],
                "groups": [],
                "error": "Search temporarily unavailable"
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class SearchUsersView(APIView):
    """Search for users only (used for adding members to groups)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response([], status=status.HTTP_200_OK)

        try:
            # Search users
            users_qs = User.objects.filter(
                Q(username__icontains=query) |
                Q(first_name__icontains=query) |
                Q(last_name__icontains=query)
            ).exclude(
                id=request.user.id
            )

            # Apply filters
            users_qs = users_qs.filter(is_approved=True, user_type=3, is_active=True)
            users = users_qs.distinct()

            serializer = UserSearchSerializer(users, many=True, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"User search error for query '{query}': {str(e)}")
            return Response([], status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class MessageSearchView(APIView):
    """Search messages within a specific conversation (private or group)"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Search messages within a specific conversation.
        Query params:
          - scope: 'private' or 'group'
          - id: other user id (for private) or group uuid (for group)
          - q: search query (required, min 1 char)
          - limit: optional max messages to scan (default 1000)
        Returns list of { id, content_snippet, timestamp, sender, match_index }
        """
        try:
            query = request.query_params.get('q', '').strip()
            scope = request.query_params.get('scope', '').strip()
            convo_id = request.query_params.get('id', '').strip()
            try:
                scan_limit = int(request.query_params.get('limit', 1000))
            except ValueError:
                scan_limit = 1000

            if not query:
                return Response([], status=status.HTTP_200_OK)

            # Because Message.content is encrypted at rest, database-level icontains filters
            # will not work. We must fetch messages for the conversation and filter in Python.
            base_qs = None

            if scope == 'private':
                try:
                    other_user = User.objects.get(id=convo_id)
                except (User.DoesNotExist, ValueError):
                    return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

                base_qs = Message.objects.filter(
                    (Q(sender=request.user, receiver=other_user) |
                     Q(sender=other_user, receiver=request.user))
                ).order_by('-timestamp')

            elif scope == 'group':
                try:
                    group = GroupChat.objects.get(id=convo_id)
                except (GroupChat.DoesNotExist, ValueError):
                    return Response({'error': 'Group not found'}, status=status.HTTP_404_NOT_FOUND)

                if request.user not in group.members.all():
                    return Response({'error': 'Not a member of this group'}, status=status.HTTP_403_FORBIDDEN)

                base_qs = Message.objects.filter(group=group).order_by('-timestamp')
            else:
                return Response({'error': 'Invalid scope'}, status=status.HTTP_400_BAD_REQUEST)

            # Limit the number of messages we scan for performance
            messages_to_scan = list(base_qs[:scan_limit])

            results = []
            q_lower = query.lower()
            for msg in messages_to_scan:
                content = (msg.content or '')
                idx = content.lower().find(q_lower)
                if idx == -1:
                    continue
                start = max(0, idx - 30)
                end = min(len(content), idx + len(query) + 30)
                snippet = content[start:end]
                if start > 0:
                    snippet = '…' + snippet
                if end < len(content):
                    snippet = snippet + '…'
                results.append({
                    'id': str(msg.id),
                    'timestamp': msg.timestamp.isoformat(),
                    'sender': {
                        'id': msg.sender.id,
                        'first_name': msg.sender.first_name,
                        'last_name': msg.sender.last_name,
                    },
                    'content_snippet': snippet,
                    'match_index': idx
                })

            # Return by chronological order (oldest first) similar to typical UX
            results.reverse()

            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error in MessageSearchView: {e}")
            return Response({'error': 'Failed to search messages'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
