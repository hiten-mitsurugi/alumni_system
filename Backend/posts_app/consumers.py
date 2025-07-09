import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


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
