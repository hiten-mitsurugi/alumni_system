"""
WebSocket consumer handlers for messaging functionality.
"""

import json
import logging
from typing import Optional, List, Dict, Any
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.db.models import Q

from messaging_app.models import Message, MessageRequest, GroupChat, MessageReaction, MessageRead, Attachment
from messaging_app.serializers import MessageSerializer

logger = logging.getLogger(__name__)
User = get_user_model()


class PrivateReactionHandlersMixin:
    """
    Mixin for private message reaction handlers.
    """
    
    async def handle_add_reaction(self, data: Dict[str, Any]):
        """Add or update emoji reaction to a message (Facebook-style)."""
        message_id = data.get('message_id')
        reaction_type = data.get('reaction_type')
        
        if not message_id or not reaction_type:
            return await self.send_json({'error': 'message_id and reaction_type are required'})
            
        try:
            @database_sync_to_async
            def _add_reaction():
                from messaging_app.models import MessageReaction
                
                # Validate reaction type
                valid_reactions = dict(MessageReaction.REACTION_CHOICES).keys()
                if reaction_type not in valid_reactions:
                    raise ValueError(f'Invalid reaction type. Valid types: {list(valid_reactions)}')
                
                message = Message.objects.get(id=message_id)
                
                # Check if user has access to this message
                has_access = False
                if message.receiver and (self.user == message.sender or self.user == message.receiver):
                    has_access = True
                elif message.group and message.group.members.filter(id=self.user.id).exists():
                    has_access = True
                
                if not has_access:
                    raise PermissionError('You do not have access to this message')
                
                # Add or update reaction (one reaction per user per message)
                reaction, created = MessageReaction.objects.update_or_create(
                    user=self.user,
                    message=message,
                    defaults={'reaction_type': reaction_type}
                )
                
                return message, reaction, created
                
            message, reaction, created = await _add_reaction()
            
            # Get updated reaction statistics
            @database_sync_to_async
            def _get_reaction_stats():
                from django.db.models import Count
                from messaging_app.models import MessageReaction
                
                # Get reaction counts by type
                reaction_counts = MessageReaction.objects.filter(
                    message=message
                ).values('reaction_type', 'emoji').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                # Get reactions by type with user info
                reactions_by_type = {}
                for reaction_type_info in MessageReaction.REACTION_CHOICES:
                    rt = reaction_type_info[0]
                    reactions = MessageReaction.objects.filter(
                        message=message,
                        reaction_type=rt
                    ).select_related('user')
                    
                    if reactions.exists():
                        reactions_by_type[rt] = {
                            'emoji': reaction_type_info[1],
                            'count': reactions.count(),
                            'users': [
                                {
                                    'id': r.user.id,
                                    'name': f"{r.user.first_name} {r.user.last_name}".strip() or r.user.username
                                }
                                for r in reactions
                            ]
                        }
                
                return {
                    'total_reactions': MessageReaction.objects.filter(message=message).count(),
                    'reaction_counts': list(reaction_counts),
                    'reactions_by_type': reactions_by_type
                }
            
            reaction_stats = await _get_reaction_stats()
            
            # Broadcast reaction update
            reaction_data = {
                'message_id': str(message.id),
                'user_id': str(self.user.id),
                'user_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
                'reaction_type': reaction_type,
                'emoji': reaction.emoji,
                'action': 'updated' if not created else 'added',
                'reaction_stats': reaction_stats,
                'timestamp': timezone.now().isoformat(),
            }
            
            # Broadcast to appropriate recipients
            if message.receiver:
                # Private message - send to both sender and receiver
                users = [message.sender.id, message.receiver.id]
                await self.broadcast_to_users(users, 'message_reaction', reaction_data)
            elif message.group:
                # Group message - send to all group members
                group_members = await database_sync_to_async(
                    lambda: list(message.group.members.values_list('id', flat=True))
                )()
                await self.broadcast_to_users(group_members, 'message_reaction', reaction_data)
            
            # Send confirmation to sender
            await self.send_json({
                'action': 'reaction_added',
                'success': True,
                'reaction': {
                    'id': str(reaction.id),
                    'reaction_type': reaction.reaction_type,
                    'emoji': reaction.emoji,
                    'created': created
                },
                'reaction_stats': reaction_stats
            })
            
        except ValueError as e:
            await self.send_json({'error': str(e)})
        except PermissionError as e:
            await self.send_json({'error': str(e)})
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found'})
        except Exception as e:
            logger.error(f"Error adding reaction: {e}")
            await self.send_json({'error': 'Failed to add reaction'})

    async def handle_remove_reaction(self, data: Dict[str, Any]):
        """Remove user's reaction from a message."""
        message_id = data.get('message_id')
        
        if not message_id:
            return await self.send_json({'error': 'message_id is required'})
            
        try:
            @database_sync_to_async
            def _remove_reaction():
                from messaging_app.models import MessageReaction
                
                message = Message.objects.get(id=message_id)
                
                # Check if user has access to this message
                has_access = False
                if message.receiver and (self.user == message.sender or self.user == message.receiver):
                    has_access = True
                elif message.group and message.group.members.filter(id=self.user.id).exists():
                    has_access = True
                
                if not has_access:
                    raise PermissionError('You do not have access to this message')
                
                # Remove user's reaction if it exists
                deleted_count = MessageReaction.objects.filter(
                    user=self.user,
                    message=message
                ).delete()[0]
                
                return message, deleted_count
                
            message, deleted_count = await _remove_reaction()
            
            if deleted_count == 0:
                return await self.send_json({'error': 'No reaction found to remove'})
            
            # Get updated reaction statistics
            @database_sync_to_async
            def _get_reaction_stats():
                from django.db.models import Count
                from messaging_app.models import MessageReaction
                
                reaction_counts = MessageReaction.objects.filter(
                    message=message
                ).values('reaction_type', 'emoji').annotate(
                    count=Count('id')
                ).order_by('-count')
                
                reactions_by_type = {}
                for reaction_type_info in MessageReaction.REACTION_CHOICES:
                    rt = reaction_type_info[0]
                    reactions = MessageReaction.objects.filter(
                        message=message,
                        reaction_type=rt
                    ).select_related('user')
                    
                    if reactions.exists():
                        reactions_by_type[rt] = {
                            'emoji': reaction_type_info[1],
                            'count': reactions.count(),
                            'users': [
                                {
                                    'id': r.user.id,
                                    'name': f"{r.user.first_name} {r.user.last_name}".strip() or r.user.username
                                }
                                for r in reactions
                            ]
                        }
                
                return {
                    'total_reactions': MessageReaction.objects.filter(message=message).count(),
                    'reaction_counts': list(reaction_counts),
                    'reactions_by_type': reactions_by_type
                }
            
            reaction_stats = await _get_reaction_stats()
            
            # Broadcast reaction removal
            reaction_data = {
                'message_id': str(message.id),
                'user_id': str(self.user.id),
                'user_name': f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
                'action': 'removed',
                'reaction_stats': reaction_stats,
                'timestamp': timezone.now().isoformat(),
            }
            
            # Broadcast to appropriate recipients
            if message.receiver:
                users = [message.sender.id, message.receiver.id]
                await self.broadcast_to_users(users, 'message_reaction', reaction_data)
            elif message.group:
                group_members = await database_sync_to_async(
                    lambda: list(message.group.members.values_list('id', flat=True))
                )()
                await self.broadcast_to_users(group_members, 'message_reaction', reaction_data)
            
            # Send confirmation to sender
            await self.send_json({
                'action': 'reaction_removed',
                'success': True,
                'reaction_stats': reaction_stats
            })
            
        except PermissionError as e:
            await self.send_json({'error': str(e)})
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found'})
        except Exception as e:
            logger.error(f"Error removing reaction: {e}")
            await self.send_json({'error': 'Failed to remove reaction'})