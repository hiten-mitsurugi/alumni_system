"""
Handler methods for private chat consumer.
Contains all handle_* methods for private messaging actions.
"""
import logging
from typing import Dict, Any, Optional
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.utils import timezone

from ..models import Message, MessageRequest, MessageReaction, BlockedUser
from .utils import parse_mentions, create_mentions, send_mention_notifications

logger = logging.getLogger(__name__)
User = get_user_model()


class PrivateMessageHandlersMixin:
    """Mixin containing all private message action handlers."""
    
    async def handle_ping(self, data: Dict[str, Any]):
        """Handle ping messages to keep connection alive."""
        await self.update_user_status(self.user, 'activity')
        await self.send_json({'action': 'pong', 'timestamp': timezone.now().isoformat()})

    async def handle_send_message(self, data: Dict[str, Any]):
        """Handle sending a private message with optional reply."""
        await self.update_user_status(self.user, 'activity')
        
        # Extract and validate data
        receiver_id = data.get('receiver_id')
        content = data.get('content', '').strip()
        attachment_ids = data.get('attachment_ids', [])
        reply_to_id = data.get('reply_to_id')
        
        # Validation
        if not receiver_id:
            return await self.send_json({'error': 'receiver_id is required'})
        if not content and not attachment_ids:
            return await self.send_json({'error': 'Message content or attachments are required'})
        if receiver_id == self.user.id:
            return await self.send_json({'error': 'Cannot send message to yourself'})
            
        try:
            receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
            
            # Check blocking status
            is_blocked_by_receiver = await self._is_user_blocked(receiver, self.user)
            is_blocked_by_sender = await self._is_user_blocked(self.user, receiver)
            
            if is_blocked_by_receiver:
                return await self.send_json({
                    'error': 'You cannot send messages to this user. You have been blocked.',
                    'blocked': True,
                    'type': 'blocked_by_them'
                })
                
            if is_blocked_by_sender:
                return await self.send_json({
                    'error': 'You cannot send messages to a user you have blocked. Please unblock them first.',
                    'blocked': True,
                    'type': 'blocked_by_me'
                })
            
            # Check if conversation exists
            conversation_exists = await self._check_conversation_exists(receiver)
            
            if not conversation_exists:
                # Create message request for new conversation
                return await self._create_message_request(receiver, content)
                
            # Create and send message
            message = await self.create_message_with_reply(receiver, content, reply_to_id)
            await self.attach_files_to_message(message, attachment_ids)
            
            # Serialize and broadcast
            serialized = await self.serialize_message(message)
            # Notify only the receiver via broadcast. The sender gets a direct
            # confirmation via `send_json` below to avoid duplicate messages
            # being delivered to the sender (once via broadcast and once via
            # direct send).
            await self.broadcast_to_users(
                [receiver.id],
                'chat_message',
                {'message': serialized}
            )
            
            # 🔔 NOTIFICATION: Broadcast notification update to receiver
            await self.channel_layer.group_send(
                f'user_{receiver.id}',
                {
                    'type': 'notification_update',
                    'data': {
                        'action': 'increment',
                        'type': 'message'
                    }
                }
            )
            
            await self.send_json({'status': 'success', 'message': serialized})
            
        except User.DoesNotExist:
            await self.send_json({'error': 'Receiver not found'})
        except Exception as e:
            logger.error(f"Error sending message: {e}", exc_info=True)
            await self.send_json({'error': f'Failed to send message: {str(e)}'})

    async def handle_bump_message(self, data: Dict[str, Any]):
        """Handle bumping a message - creates a new message referencing the original."""
        await self.update_user_status(self.user, 'activity')
        
        # Extract data
        original_message_id = data.get('original_message_id')
        receiver_id = data.get('receiver_id')
        
        # Validation
        if not original_message_id:
            return await self.send_json({'error': 'original_message_id is required'})
        if not receiver_id:
            return await self.send_json({'error': 'receiver_id is required'})
        if receiver_id == self.user.id:
            return await self.send_json({'error': 'Cannot bump message to yourself'})
            
        try:
            # Get receiver user
            try:
                receiver = await database_sync_to_async(User.objects.get)(id=receiver_id)
            except User.DoesNotExist:
                return await self.send_json({'error': 'Receiver not found'})
            
            # Check if conversation exists
            conversation_exists = await self._check_conversation_exists(receiver)
            if not conversation_exists:
                return await self.send_json({'error': 'No active conversation with this user'})
            
            # Create bump message
            bump_message = await self._create_bump_message(receiver, original_message_id)
            
            # Serialize and broadcast
            serialized = await self.serialize_message(bump_message)
            
            # Broadcast only to receiver; send confirmation directly to sender
            # to prevent the sender receiving the same message twice.
            await self.broadcast_to_users([receiver.id], 'chat_message', {'message': serialized})
            await self.send_json({'status': 'success', 'message': serialized})
            
        except ValueError as ve:
            logger.error(f"Validation error in bump: {ve}")
            await self.send_json({'error': str(ve)})
        except Exception as e:
            logger.error(f"Unexpected error bumping message: {e}")
            await self.send_json({'error': 'Failed to bump message'})

    async def handle_add_reaction(self, data: Dict[str, Any]):
        """Add or update emoji reaction to a message (Facebook-style)."""
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
            reaction_stats = await self.get_reaction_stats(message)
            
            # Broadcast reaction update
            await self.broadcast_reaction_update(
                message, 
                self.user.id, 
                f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
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
            reaction_stats = await self.get_reaction_stats(message)
            
            # Broadcast reaction removal
            await self.broadcast_reaction_update(
                message,
                self.user.id,
                f"{self.user.first_name} {self.user.last_name}".strip() or self.user.username,
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
            logger.error(f"Error removing reaction: {e}")
            await self.send_json({'error': 'Failed to remove reaction'})

    async def handle_edit_message(self, data: Dict[str, Any]):
        """Edit user's own message."""
        message_id = data.get('message_id')
        new_content = data.get('new_content', '').strip()
        
        logger.info(f"Edit request: message_id={message_id}, new_content='{new_content}', user={self.user.id}")
        
        if not message_id or not new_content:
            logger.warning(f"Edit validation failed: message_id={message_id}, new_content='{new_content}'")
            return await self.send_json({'error': 'message_id and new_content are required'})
            
        try:
            @database_sync_to_async
            def _edit():
                logger.info(f"Looking for message with id={message_id} and sender={self.user.id}")
                message = Message.objects.get(id=message_id, sender=self.user)
                logger.info(f"Found message: {message.id}, current content: '{message.content}'")
                message.content = new_content
                message.edited_at = timezone.now()  # Set edit timestamp
                message.save()
                logger.info(f"Message saved successfully with new content: '{message.content}'")
                
                # Get user IDs for broadcasting - must be done in sync context
                users = [message.sender.id, message.receiver.id] if message.receiver else [message.sender.id]
                return message, message.edited_at, users
                
            message, edited_at, users = await _edit()
            
            # Broadcast to participants (exclude sender to avoid duplicate
            # delivery since we send a direct confirmation below)
            logger.info(f"Broadcasting edit to users: {users}")
            recipients = [uid for uid in users if uid != self.user.id]
            if recipients:
                await self.broadcast_to_users(
                    recipients,
                    'message_edited',
                    {
                        'message_id': str(message.id),
                        'new_content': new_content,
                        'edited_at': edited_at.isoformat()
                    }
                )
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_edited',
                'message_id': str(message.id)
            })
            logger.info(f"Edit completed successfully for message {message.id}")
            
        except Message.DoesNotExist:
            logger.error(f"Message not found: id={message_id}, sender={self.user.id}")
            await self.send_json({'error': 'Cannot edit this message'})
        except Exception as e:
            logger.error(f"Error editing message {message_id}: {e}", exc_info=True)
            await self.send_json({'error': 'Failed to edit message'})

    async def handle_delete_message(self, data: Dict[str, Any]):
        """Delete user's own message."""
        message_id = data.get('message_id')
        
        if not message_id:
            return await self.send_json({'error': 'message_id is required'})
            
        try:
            @database_sync_to_async
            def _delete():
                message = Message.objects.get(id=message_id, sender=self.user)
                users = [message.sender.id, message.receiver.id] if message.receiver else [message.sender.id]
                message.delete()
                return users
                
            users = await _delete()
            
            # Exclude sender to avoid duplicate notification on sender side
            recipients = [uid for uid in users if uid != self.user.id]
            if recipients:
                await self.broadcast_to_users(
                    recipients,
                    'message_deleted',
                    {'message_id': str(message_id)}
                )
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_deleted',
                'message_id': str(message_id)
            })
            
        except Message.DoesNotExist:
            await self.send_json({'error': 'Cannot delete this message'})

    async def handle_pin_message(self, data: Dict[str, Any]):
        """Pin or unpin user's own message or messages in conversation."""
        message_id = data.get('message_id')
        
        logger.info(f"Pin request: message_id={message_id}, user={self.user.id}")
        
        if not message_id:
            logger.warning(f"Pin validation failed: message_id={message_id}")
            return await self.send_json({'error': 'message_id is required'})
            
        try:
            @database_sync_to_async
            def _pin():
                logger.info(f"Looking for message with id={message_id}")
                
                # Get the message - allow pinning for conversation participants
                message = Message.objects.get(id=message_id)
                
                # Check permissions
                can_pin = False
                if message.receiver:  # Private message
                    if self.user == message.sender or self.user == message.receiver:
                        can_pin = True
                elif message.group:  # Group message
                    if self.user in message.group.members.all():
                        can_pin = True
                
                if not can_pin:
                    raise PermissionError("No permission to pin this message")
                
                logger.info(f"Found message: {message.id}, current pin status: {message.is_pinned}")
                
                # Toggle pin status
                message.is_pinned = not message.is_pinned
                message.save()
                
                logger.info(f"Message pin status updated to: {message.is_pinned}")
                
                # Get user IDs for broadcasting - must be done in sync context
                if message.receiver:
                    users = [message.sender.id, message.receiver.id]
                else:
                    # For group messages, get all group members
                    users = list(message.group.members.values_list('id', flat=True))
                
                return message, message.is_pinned, users
                
            message, is_pinned, users = await _pin()
            
            # Broadcast to participants (exclude sender to avoid duplicate
            # delivery since we send a direct confirmation below)
            logger.info(f"Broadcasting pin update to users: {users}")
            recipients = [uid for uid in users if uid != self.user.id]
            if recipients:
                await self.broadcast_to_users(
                    recipients,
                    'message_pinned',
                    {
                        'message_id': str(message.id),
                        'is_pinned': is_pinned,
                        'action': 'pin' if is_pinned else 'unpin'
                    }
                )
            
            # Send success confirmation to sender
            await self.send_json({
                'status': 'success', 
                'action': 'message_pinned',
                'message_id': str(message.id),
                'is_pinned': is_pinned
            })
            logger.info(f"Pin completed successfully for message {message.id}")
            
        except Message.DoesNotExist:
            logger.error(f"Message not found: id={message_id}")
            await self.send_json({'error': 'Message not found'})
        except PermissionError as e:
            logger.error(f"Permission denied for pin: {e}")
            await self.send_json({'error': 'You do not have permission to pin this message'})
        except Exception as e:
            logger.error(f"Error pinning message {message_id}: {e}", exc_info=True)
            await self.send_json({'error': 'Failed to pin message'})

    async def handle_mark_as_read(self, data: Dict[str, Any]):
        """Mark messages from specific user as read."""
        receiver_id = data.get('receiver_id')
        
        if not receiver_id:
            return
            
        @database_sync_to_async
        def _mark_read():
            # Count how many messages will be marked as read
            unread_count = Message.objects.filter(
                sender_id=receiver_id, 
                receiver=self.user, 
                is_read=False
            ).count()
            
            # Mark messages as read
            Message.objects.filter(
                sender_id=receiver_id, 
                receiver=self.user, 
                is_read=False
            ).update(is_read=True)
            
            return unread_count
            
        marked_count = await _mark_read()
        
        # 🔔 NOTIFICATION: Send notification update to decrement unread count
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
            
            # Also invalidate cache for this user
            from django.core.cache import cache
            cache.delete(f"unread_counts_{self.user.id}")
        
        await self.broadcast_to_users(
            [receiver_id], 
            'messages_read', 
            {'receiver_id': str(self.user.id)}
        )

    async def handle_typing(self, data: Dict[str, Any]):
        """Notify typing status."""
        receiver_id = data.get('receiver_id')
        if receiver_id:
            await self.broadcast_to_users(
                [receiver_id], 
                'user_typing', 
                {'user_id': self.user.id}
            )

    async def handle_stop_typing(self, data: Dict[str, Any]):
        """Notify stop typing."""
        receiver_id = data.get('receiver_id')
        if receiver_id:
            await self.broadcast_to_users(
                [receiver_id], 
                'user_stop_typing', 
                {'user_id': self.user.id}
            )
