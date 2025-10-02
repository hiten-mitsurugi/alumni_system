from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache

from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from ..models import Message, GroupChat, MessageRequest, BlockedUser, GroupMemberRequest, MessageRead
from ..serializers import UserSerializer, GroupChatSerializer, MessageSerializer, MessageRequestSerializer, BlockedUserSerializer, AttachmentSerializer, ReactionSerializer, UserSearchSerializer, GroupMemberRequestSerializer
from ..link_utils import create_link_previews_for_message
import logging
from django.conf import settings
from django.core.files.storage import FileSystemStorage
import uuid

# Initialize logger
logger = logging.getLogger(__name__)
from ..models import Attachment
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)

class MessageSearchView(APIView):
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


# === MESSAGE REACTIONS VIEWS ===
