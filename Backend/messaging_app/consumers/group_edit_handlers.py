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


class GroupEditHandlersMixin:
    """
    Mixin for group message editing and deletion handlers.
    """
    
    async def handle_group_edit(self, data: Dict[str, Any]):
        """Edit group message (own messages only)."""
        message_id = data.get('message_id')
        new_content = data.get('new_content', '').strip()
        
        if not message_id or not new_content:
            return await self.send_json({'error': 'message_id and new_content are required'})
            
        try:
            @database_sync_to_async
            def _edit():
                from django.utils import timezone as tz
                message = Message.objects.get(
                    id=message_id, 
                    group_id=self.group_id, 
                    sender=self.user
                )
                message.content = new_content
                message.edited_at = tz.now()  # Set edit timestamp
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