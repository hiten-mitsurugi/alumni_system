import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class PostDetailConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for individual post real-time updates"""
    
    async def connect(self):
        """Handle connection to specific post"""
        self.user = self.scope["user"]
        self.post_id = self.scope['url_route']['kwargs']['post_id']
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Check if user can view this post
        can_view = await self.check_post_permissions(self.post_id, self.user)
        if not can_view:
            await self.close()
            return
        
        # Join post-specific group
        self.post_group_name = f'post_{self.post_id}'
        await self.channel_layer.group_add(
            self.post_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connected_to_post',
            'post_id': self.post_id,
            'message': f'Connected to post {self.post_id} for real-time updates'
        }))
    
    async def disconnect(self, close_code):
        """Handle disconnection from post"""
        await self.channel_layer.group_discard(
            self.post_group_name,
            self.channel_name
        )
    
    @database_sync_to_async
    def check_post_permissions(self, post_id, user):
        """Check if user can view the post"""
        from ..models import Post
        
        try:
            post = Post.objects.get(id=post_id)
            
            # Admins can see all posts
            if user.user_type in [1, 2]:
                return True
            
            # Users can see their own posts
            if post.user == user:
                return True
            
            # Only approved posts for others
            if not post.is_approved:
                return False
            
            # Check visibility
            if post.visibility == 'admin_only' and user.user_type not in [1, 2]:
                return False
            
            return True
            
        except Post.DoesNotExist:
            return False
    
    async def receive(self, text_data):
        """Handle incoming messages for post"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'typing_start':
                # Broadcast typing indicator
                await self.channel_layer.group_send(
                    self.post_group_name,
                    {
                        'type': 'typing_indicator',
                        'user_id': self.user.id,
                        'user_name': f"{self.user.first_name} {self.user.last_name}",
                        'is_typing': True
                    }
                )
            
            elif message_type == 'typing_stop':
                # Stop typing indicator
                await self.channel_layer.group_send(
                    self.post_group_name,
                    {
                        'type': 'typing_indicator',
                        'user_id': self.user.id,
                        'user_name': f"{self.user.first_name} {self.user.last_name}",
                        'is_typing': False
                    }
                )
                
        except json.JSONDecodeError:
            pass
    
    # Group message handlers for post-specific events
    async def reaction_update(self, event):
        """Handle reaction updates"""
        await self.send(text_data=json.dumps(event))
    
    async def new_comment(self, event):
        """Handle new comments"""
        await self.send(text_data=json.dumps(event))
    
    async def typing_indicator(self, event):
        """Handle typing indicators"""
        # Don't send typing indicator to the user who is typing
        if event['user_id'] != self.user.id:
            await self.send(text_data=json.dumps({
                'type': 'typing_indicator',
                'user_id': event['user_id'],
                'user_name': event['user_name'],
                'is_typing': event['is_typing']
            }))