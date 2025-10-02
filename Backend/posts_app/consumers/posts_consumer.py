import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class PostsConsumer(AsyncWebsocketConsumer):
    """WebSocket consumer for real-time post updates"""
    
    async def connect(self):
        """Handle WebSocket connection"""
        self.user = self.scope["user"]
        
        # Initialize group names to prevent AttributeError
        self.posts_group_name = None
        self.user_group_name = None
        self.admin_group_name = None
        
        if not self.user.is_authenticated:
            await self.close()
            return
        
        # Join main posts feed group
        self.posts_group_name = 'posts_feed'
        await self.channel_layer.group_add(
            self.posts_group_name,
            self.channel_name
        )
        
        # Join user-specific group for notifications
        self.user_group_name = f'user_{self.user.id}'
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        
        # Join admin notifications if user is admin
        if self.user.user_type in [1, 2]:  # Admin or SuperAdmin
            self.admin_group_name = 'admin_notifications'
            await self.channel_layer.group_add(
                self.admin_group_name,
                self.channel_name
            )
        
        await self.accept()
        
        # Send connection confirmation
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Connected to posts feed',
            'user_id': self.user.id,
            'timestamp': timezone.now().isoformat()
        }))
    
    async def disconnect(self, close_code):
        """Handle WebSocket disconnection"""
        # Leave posts group
        if hasattr(self, 'posts_group_name') and self.posts_group_name:
            await self.channel_layer.group_discard(
                self.posts_group_name,
                self.channel_name
            )
        
        # Leave user group
        if hasattr(self, 'user_group_name') and self.user_group_name:
            await self.channel_layer.group_discard(
                self.user_group_name,
                self.channel_name
            )
        
        # Leave admin group if applicable
        if hasattr(self, 'admin_group_name') and self.admin_group_name:
            await self.channel_layer.group_discard(
                self.admin_group_name,
                self.channel_name
            )
    
    async def receive(self, text_data):
        """Handle incoming WebSocket messages"""
        try:
            data = json.loads(text_data)
            message_type = data.get('type')
            
            if message_type == 'join_post':
                # Join specific post group for real-time comments/reactions
                post_id = data.get('post_id')
                if post_id:
                    post_group_name = f'post_{post_id}'
                    await self.channel_layer.group_add(
                        post_group_name,
                        self.channel_name
                    )
                    
                    await self.send(text_data=json.dumps({
                        'type': 'joined_post',
                        'post_id': post_id,
                        'message': f'Joined post {post_id} for real-time updates'
                    }))
            
            elif message_type == 'leave_post':
                # Leave specific post group
                post_id = data.get('post_id')
                if post_id:
                    post_group_name = f'post_{post_id}'
                    await self.channel_layer.group_discard(
                        post_group_name,
                        self.channel_name
                    )
                    
                    await self.send(text_data=json.dumps({
                        'type': 'left_post',
                        'post_id': post_id,
                        'message': f'Left post {post_id} updates'
                    }))
            
            elif message_type == 'ping':
                # Handle ping for connection keep-alive
                await self.send(text_data=json.dumps({
                    'type': 'pong',
                    'timestamp': timezone.now().isoformat()
                }))
                
        except json.JSONDecodeError:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': 'Invalid JSON format'
            }))
        except Exception as e:
            await self.send(text_data=json.dumps({
                'type': 'error',
                'message': f'Error processing message: {str(e)}'
            }))
    
    # Group message handlers
    async def new_post(self, event):
        """Handle new post broadcast"""
        await self.send(text_data=json.dumps({
            'type': 'new_post',
            'post_id': event['post_id'],
            'user_id': event['user_id'],
            'timestamp': event['timestamp'],
            'message': 'New post available'
        }))
    
    async def post_pending_approval(self, event):
        """Handle new post pending approval (admin only)"""
        if self.user.user_type in [1, 2]:  # Only for admins
            await self.send(text_data=json.dumps({
                'type': 'post_pending_approval',
                'post_id': event['post_id'],
                'user': event['user'],
                'title': event['title'],
                'timestamp': event['timestamp'],
                'message': f"New post by {event['user']} needs approval"
            }))
    
    async def reaction_update(self, event):
        """Handle reaction updates on posts"""
        await self.send(text_data=json.dumps({
            'type': 'reaction_update',
            'post_id': event['post_id'],
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'reaction_type': event['reaction_type'],
            'action': event['action'],
            'timestamp': event['timestamp']
        }))
    
    async def new_comment(self, event):
        """Handle new comment on posts"""
        await self.send(text_data=json.dumps({
            'type': 'new_comment',
            'post_id': event['post_id'],
            'comment_id': event['comment_id'],
            'user_id': event['user_id'],
            'user_name': event['user_name'],
            'content': event['content'],
            'parent_id': event.get('parent_id'),
            'timestamp': event['timestamp']
        }))
    
    async def post_shared(self, event):
        """Handle post sharing notifications"""
        if self.user.id == event.get('original_author_id'):
            await self.send(text_data=json.dumps({
                'type': 'post_shared',
                'original_post_id': event['original_post_id'],
                'shared_post_id': event['shared_post_id'],
                'sharer_id': event['sharer_id'],
                'sharer_name': event['sharer_name'],
                'timestamp': event['timestamp'],
                'message': f"{event['sharer_name']} shared your post"
            }))
    
    async def post_approval_update(self, event):
        """Handle post approval/rejection updates"""
        await self.send(text_data=json.dumps({
            'type': 'post_approval_update',
            'post_id': event['post_id'],
            'approved': event['approved'],
            'admin_name': event['admin_name'],
            'timestamp': event['timestamp'],
            'message': f"Your post was {'approved' if event['approved'] else 'rejected'} by {event['admin_name']}"
        }))
    
    async def notification(self, event):
        """Handle general notifications"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'timestamp': timezone.now().isoformat()
        }))