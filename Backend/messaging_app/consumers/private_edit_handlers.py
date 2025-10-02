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


class PrivateEditHandlersMixin:
    """
    Mixin for private message editing and deletion handlers.
    """
    
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
                from django.utils import timezone as tz
                logger.info(f"Looking for message with id={message_id} and sender={self.user.id}")
                message = Message.objects.get(id=message_id, sender=self.user)
                logger.info(f"Found message: {message.id}, current content: '{message.content}'")
                message.content = new_content
                message.edited_at = tz.now()  # Set edit timestamp
                message.save()
                logger.info(f"Message saved successfully with new content: '{message.content}'")
                
                # Get user IDs for broadcasting - must be done in sync context
                users = [message.sender.id, message.receiver.id] if message.receiver else [message.sender.id]
                return message, message.edited_at, users
                
            message, edited_at, users = await _edit()
            
            # Broadcast to participants
            logger.info(f"Broadcasting edit to users: {users}")
            await self.broadcast_to_users(
                users,
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
            
            await self.broadcast_to_users(
                users,
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