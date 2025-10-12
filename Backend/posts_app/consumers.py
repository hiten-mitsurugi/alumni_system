import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.core.cache import cache
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
    
    async def post_deleted(self, event):
        """Handle post deletion broadcasts"""
        await self.send(text_data=json.dumps({
            'type': 'post_deleted',
            'post_id': event['post_id'],
            'deleted_by_user_id': event['deleted_by_user_id'],
            'deleted_by_name': event['deleted_by_name'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
    async def notification(self, event):
        """Handle general notifications"""
        await self.send(text_data=json.dumps({
            'type': 'notification',
            'message': event['message'],
            'timestamp': timezone.now().isoformat()
        }))

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
        from .models import Post
        
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
    
    async def post_deleted(self, event):
        """Handle post deletion"""
        await self.send(text_data=json.dumps({
            'type': 'post_deleted',
            'post_id': event['post_id'],
            'deleted_by_user_id': event['deleted_by_user_id'],
            'deleted_by_name': event['deleted_by_name'],
            'message': event['message'],
            'timestamp': event['timestamp']
        }))
    
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

# Legacy consumer for backward compatibility
class PostConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if not self.user.is_authenticated:
            await self.close(code=4001)
            return
        self.post_id = self.scope['url_route']['kwargs'].get('post_id')
        if self.post_id:
            self.group_name = f'post_{self.post_id}'
            await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.channel_layer.group_add('notifications', self.channel_name)
        await self.accept()

    async def disconnect(self, _):
        if hasattr(self, 'group_name'):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
        await self.channel_layer.group_discard('notifications', self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        if message_type == 'comment':
            content = data['content']
            parent_id = data.get('parent_id')
            comment = await self.save_comment(content, parent_id)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'new_comment',
                    'comment': {
                        'id': comment.id,
                        'user': self.user.email,
                        'content': content,
                        'parent_id': parent_id,
                        'timestamp': comment.created_at.isoformat(),
                        'reactions': [],
                    }
                }
            )
        elif message_type == 'reaction':
            reaction_type = data['reaction_type']
            content_type = data['content_type']
            object_id = data['object_id']
            reaction = await self.save_reaction(reaction_type, content_type, object_id)
            await self.channel_layer.group_send(
                self.group_name,
                {
                    'type': 'new_reaction',
                    'reaction': {
                        'id': reaction.id,
                        'user': self.user.email,
                        'reaction_type': reaction_type,
                        'content_type': content_type,
                        'object_id': object_id,
                        'timestamp': reaction.created_at.isoformat(),
                    }
                }
            )

    async def new_comment(self, event):
        await self.send(text_data=json.dumps({'type': 'new_comment', 'comment': event['comment']}))

    async def new_reaction(self, event):
        await self.send(text_data=json.dumps({'type': 'new_reaction', 'reaction': event['reaction']}))

    @database_sync_to_async
    def save_comment(self, content, parent_id=None):
        from .models import Post, Comment  # moved inside
        post = Post.objects.get(id=self.post_id)
        parent = Comment.objects.get(id=parent_id) if parent_id else None
        return Comment.objects.create(user=self.user, post=post, content=content, parent=parent)

    @database_sync_to_async
    def save_reaction(self, reaction_type, content_type_str, object_id):
        from django.contrib.contenttypes.models import ContentType
        from .models import Reaction  # moved inside
        content_type = ContentType.objects.get(model=content_type_str)
        reaction, _ = Reaction.objects.get_or_create(
            user=self.user,
            content_type=content_type,
            object_id=object_id,
            reaction_type=reaction_type
        )
        return reaction
