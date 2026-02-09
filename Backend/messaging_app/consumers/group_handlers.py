"""
Handler methods for group chat consumer.
Contains all handle_group_* methods for group messaging actions.
"""
import logging
from typing import Dict, Any
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

from ..models import Message, GroupChat, MessageReaction, MessageRead
from .utils import create_mentions, send_mention_notifications

logger = logging.getLogger(__name__)
User = get_user_model()


class GroupMessageHandlersMixin:
    """Mixin containing all group message action handlers."""
    
    async def handle_ping(self, data: Dict[str, Any]):
        """Handle ping messages to keep connection alive."""
        await self.update_user_status(self.user, 'activity')
        await self.send_json({'action': 'pong', 'timestamp': timezone.now().isoformat()})

    async def handle_group_message(self, data: Dict[str, Any]):
        """Send message to group with optional reply."""
        await self.update_user_status(self.user, 'activity')
        
        content = data.get('content', '').strip()
        attachment_ids = data.get('attachment_ids', [])
        reply_to_id = data.get('reply_to_id')
        
        if not content and not attachment_ids:
            return await self.send_json({'error': 'Message content or attachments are required'})
            
        try:
            # Create message using base class method
            message = await self._create_group_message(content, reply_to_id)
            await self.attach_files_to_message(message, attachment_ids)
            
            # Process @mentions in group messages
            mentioned_users = await create_mentions(message, content, self.group)
            if mentioned_users:
                logger.info(f"Created mentions for {len(mentioned_users)} users in group message {message.id}")
                await send_mention_notifications(self.channel_layer, mentioned_users, message, self.group)
            
            # Invalidate Redis caches after sending group message
            await self._invalidate_group_caches()
            
            # Serialize and broadcast to group
            serialized = await self.serialize_message(message)
            await self.channel_layer.group_send(
                self.group_name, 
                {'type': 'chat_message', 'message': serialized}
            )
            
            # Notify group members on personal channels for unread counters
            await self._send_group_message_notifications(message)
            
        except Exception as e:
            logger.error(f"Error sending group message: {e}", exc_info=True)
            await self.send_json({'error': f'Failed to send group message: {str(e)}'})

    async def _create_group_message(self, content: str, reply_to_id: str = None):
        """Create a group message with optional reply."""
        @database_sync_to_async
        def _create():
            # Get reply message if specified
            reply_to = None
            if reply_to_id:
                try:
                    reply_to = Message.objects.get(id=reply_to_id)
                except Message.DoesNotExist:
                    pass
                    
            # Create group message
            message = Message.objects.create(
                sender=self.user,
                group=self.group,
                content=content,
                reply_to=reply_to
            )
            
            # Return with relationships
            return Message.objects.select_related(
                'sender', 'group', 'reply_to', 'reply_to__sender'
            ).prefetch_related('attachments').get(id=message.id)
            
        return await _create()

    async def _invalidate_group_caches(self):
        """Invalidate Redis caches for group conversation."""
        @database_sync_to_async
        def _invalidate():
            from django.core.cache import cache
            
            # Clear group conversation caches for all members
            for member in self.group.members.all():
                cache.delete(f"user_conversations_{member.id}")
                cache.delete(f"group_messages_{self.group.id}_{member.id}")
            
            logger.info(f"Cache invalidated after group message sent to group {self.group.id}")
        
        await _invalidate()

    async def _send_group_message_notifications(self, message: Message):
        """Send notifications to group members for new message."""
        try:
            from asgiref.sync import async_to_sync
            from channels.layers import get_channel_layer
            channel_layer = get_channel_layer()
            
            @database_sync_to_async
            def _member_ids():
                return list(self.group.members.values_list('id', flat=True))
            
            members = await _member_ids()
            preview = {
                'id': str(message.id),
                'group': str(self.group.id),
                'content': message.content,
                'timestamp': message.timestamp.isoformat(),
                'sender': {
                    'id': self.user.id,
                    'first_name': self.user.first_name,
                    'last_name': self.user.last_name,
                }
            }
            for member_id in members:
                # Skip sender
                if member_id == self.user.id:
                    continue
                async_to_sync(channel_layer.group_send)(
                    f'user_{member_id}',
                    {
                        'type': 'group_message_preview',
                        'message': preview
                    }
                )
                # Send notification update for navbar badge
                async_to_sync(channel_layer.group_send)(
                    f'user_{member_id}',
                    {
                        'type': 'notification_update',
                        'data': {
                            'action': 'increment',
                            'type': 'message'
                        }
                    }
                )
        except Exception as notify_err:
            logger.error(f"Failed to send group message preview notifications: {notify_err}")

    async def handle_group_bump(self, data: Dict[str, Any]):
        """Handle bumping a message in group chat."""
        await self.update_user_status(self.user, 'activity')
        
        original_message_id = data.get('original_message_id')
        
        if not original_message_id:
            return await self.send_json({'error': 'original_message_id is required'})
            
        try:
            @database_sync_to_async
            def _create_group_bump():
                # Get the original message
                try:
                    original_message = Message.objects.get(
                        id=original_message_id,
                        group_id=self.group_id
                    )
                except Message.DoesNotExist:
                    raise ValueError("Original message not found in this group")
                
                # Create bump message
                message = Message.objects.create(
                    sender=self.user,
                    group=self.group,
                    content="🔔 Bumped message",
                    reply_to=original_message
                )
                
                # Return with relationships
                return Message.objects.select_related(
                    'sender', 'group', 'reply_to', 'reply_to__sender'
                ).prefetch_related('attachments').get(id=message.id)
                
            message = await _create_group_bump()
            
            # Serialize and broadcast to group
            serialized = await self.serialize_message(message)
            await self.channel_layer.group_send(
                self.group_name, 
                {'type': 'chat_message', 'message': serialized}
            )
            
        except ValueError as e:
            await self.send_json({'error': str(e)})
        except Exception as e:
            logger.error(f"Error bumping group message: {e}")
            await self.send_json({'error': 'Failed to bump message'})

    async def handle_group_reaction(self, data: Dict[str, Any]):
        """Add or update reaction to group message (Facebook-style)."""
        message_id = data.get('message_id')
        reaction_type = data.get('reaction_type')
        
        if not message_id or not reaction_type:
            return await self.send_json({'error': 'message_id and reaction_type are required'})
            
        try:
            @database_sync_to_async
            def _add_reaction():
                # Validate reaction type
                valid_reactions = dict(MessageReaction.REACTION_CHOICES).keys()
                if reaction_type not in valid_reactions:
                    raise ValueError(f'Invalid reaction type. Valid types: {list(valid_reactions)}')
                
                message = Message.objects.get(id=message_id, group_id=self.group_id)
                
                # Check if user is a member of the group
                if not message.group.members.filter(id=self.user.id).exists():
                    raise PermissionError('You are not a member of this group')
                
                # Add or update reaction
                reaction, created = MessageReaction.objects.update_or_create(
                    user=self.user,
                    message=message,
                    defaults={'reaction_type': reaction_type}
                )
                
                return message, reaction, created
                
            message, reaction, created = await _add_reaction()
            
            # Get updated reaction statistics using base class method
            reaction_stats = await self.get_reaction_stats(message)
            
            # Broadcast to group members using base class method
            await self.broadcast_reaction_update(
                message=message,
                user_id=self.user.id,
                user_name=f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
                reaction_type=reaction_type,
                emoji=reaction.emoji,
                action='updated' if not created else 'added',
                reaction_stats=reaction_stats
            )
            
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
            logger.error(f"Error adding group reaction: {e}")
            await self.send_json({'error': 'Failed to add reaction'})

    async def handle_group_remove_reaction(self, data: Dict[str, Any]):
        """Remove user's reaction from group message."""
        message_id = data.get('message_id')
        
        if not message_id:
            return await self.send_json({'error': 'message_id is required'})
            
        try:
            @database_sync_to_async
            def _remove_reaction():
                message = Message.objects.get(id=message_id, group_id=self.group_id)
                
                # Check if user is a member of the group
                if not message.group.members.filter(id=self.user.id).exists():
                    raise PermissionError('You are not a member of this group')
                
                # Remove user's reaction if it exists
                deleted_count = MessageReaction.objects.filter(
                    user=self.user,
                    message=message
                ).delete()[0]
                
                return message, deleted_count
                
            message, deleted_count = await _remove_reaction()
            
            if deleted_count == 0:
                return await self.send_json({'error': 'No reaction found to remove'})
            
            # Get updated reaction statistics using base class method
            reaction_stats = await self.get_reaction_stats(message)
            
            # Broadcast to group members using base class method
            await self.broadcast_reaction_update(
                message=message,
                user_id=self.user.id,
                user_name=f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
                action='removed',
                reaction_stats=reaction_stats
            )
            
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
            logger.error(f"Error removing group reaction: {e}")
            await self.send_json({'error': 'Failed to remove reaction'})

    async def handle_group_edit(self, data: Dict[str, Any]):
        """Edit group message (own messages only)."""
        message_id = data.get('message_id')
        new_content = data.get('new_content', '').strip()
        
        if not message_id or not new_content:
            return await self.send_json({'error': 'message_id and new_content are required'})
            
        try:
            @database_sync_to_async
            def _edit():
                message = Message.objects.get(
                    id=message_id, 
                    group_id=self.group_id, 
                    sender=self.user
                )
                message.content = new_content
                message.edited_at = timezone.now()
                message.save()
                return message.edited_at
                
            edited_at = await _edit()
            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'message_edited',
                    'message_id': str(message_id),
                    'new_content': new_content,
                    'edited_at': edited_at.isoformat()
                }
            )
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_edited',
                'message_id': str(message_id)
            })
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot edit this message'})
        except Exception as e:
            logger.error(f"Error editing group message: {e}")
            await self.send_json({'error': 'Failed to edit message'})

    async def handle_group_delete(self, data: Dict[str, Any]):
        """Delete group message (own messages only)."""
        message_id = data.get('message_id')
        
        if not message_id:
            return await self.send_json({'error': 'message_id is required'})
            
        try:
            @database_sync_to_async
            def _delete():
                message = Message.objects.get(
                    id=message_id, 
                    group_id=self.group_id, 
                    sender=self.user
                )
                message.delete()
                
            await _delete()
            
            await self.channel_layer.group_send(
                self.group_name,
                {'type': 'message_deleted', 'message_id': str(message_id)}
            )
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_deleted',
                'message_id': str(message_id)
            })
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot delete this message'})

    async def handle_group_pin(self, data: Dict[str, Any]):
        """Pin or unpin group message (any group member can pin)."""
        message_id = data.get('message_id')
        
        if not message_id:
            return await self.send_json({'error': 'message_id is required'})
            
        try:
            @database_sync_to_async
            def _pin():
                message = Message.objects.get(
                    id=message_id, 
                    group_id=self.group_id
                )
                
                # Toggle pin status
                message.is_pinned = not message.is_pinned
                message.save()
                return message.is_pinned
                
            is_pinned = await _pin()
            
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'message_pinned',
                    'message_id': str(message_id),
                    'is_pinned': is_pinned,
                    'action': 'pin' if is_pinned else 'unpin'
                }
            )
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_pinned',
                'message_id': str(message_id),
                'is_pinned': is_pinned
            })
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Message not found in this group'})
        except Exception as e:
            logger.error(f"Error pinning group message: {e}")
            await self.send_json({'error': 'Failed to pin message'})

    async def handle_group_typing(self, data: Dict[str, Any]):
        """Notify group of typing."""
        await self.channel_layer.group_send(
            self.group_name, 
            {'type': 'user_typing', 'user_id': self.user.id}
        )

    async def handle_group_stop_typing(self, data: Dict[str, Any]):
        """Notify group of stop typing."""
        await self.channel_layer.group_send(
            self.group_name, 
            {'type': 'user_stop_typing', 'user_id': self.user.id}
        )

    async def handle_group_mark_as_read(self, data: Dict[str, Any]):
        """Mark group messages as read for the current user."""
        group_id = data.get('group_id')
        
        if not group_id or str(group_id) != str(self.group_id):
            return
            
        @database_sync_to_async
        def _mark_group_read():
            # Get all unread messages in this group from other users
            unread_messages = Message.objects.filter(
                group_id=group_id
            ).exclude(sender=self.user)
            
            marked_count = 0
            # Only mark messages as read that don't already have a MessageRead record
            for message in unread_messages:
                msg_read_obj, created = MessageRead.objects.get_or_create(
                    message=message,
                    user=self.user,
                    defaults={'read_at': timezone.now()}
                )
                if created:
                    marked_count += 1
            
            return marked_count
            
        marked_count = await _mark_group_read()
        
        # Send notification update to decrement unread count
        if marked_count > 0:
            await self.channel_layer.group_send(
                f'user_{self.user.id}',
                {
                    'type': 'notification_update',
                    'data': {
                        'action': 'decrement',
                        'type': 'message',
                        'count': marked_count
                    }
                }
            )
            
            # Invalidate cache for this user
            from django.core.cache import cache
            cache.delete(f"unread_counts_{self.user.id}")
        
        # Notify other group members that this user has read messages
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'group_messages_read',
                'user_id': self.user.id,
                'group_id': str(group_id)
            }
        )
