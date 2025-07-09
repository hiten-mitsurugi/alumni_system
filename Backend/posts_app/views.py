from django.contrib.contenttypes.models import ContentType
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Post, Comment, Reaction
from .serializers import PostSerializer, CommentSerializer, ReactionSerializer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class IsAdminOrSuperAdmin:
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.user_type in [1, 2]  # 1=Admin, 2=SuperAdmin

class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        category = request.query_params.get('category')
        posts = Post.objects.filter(is_approved=True)
        if category:
            posts = posts.filter(content_category=category)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            is_approved = user.user_type in [1, 2]
            serializer.save(user=user, is_approved=is_approved)
            if not is_approved:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'admin_notifications',
                    {'type': 'notification', 'message': f'New post by {user.email} awaits approval.'}
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = PostSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            is_approved = user.user_type in [1, 2]
            serializer.save(user=user, is_approved=is_approved)
            if not is_approved:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    'admin_notifications',
                    {'type': 'notification', 'message': f'New post by {user.email} awaits approval.'}
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PostDetailView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]  # Restrict to admins/superadmins

    def get(self, request, post_id):
        try:
            post = Post.objects.get(pk=post_id)
            serializer = PostSerializer(post)
            return Response(serializer.data)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

class CommentListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        comments = Comment.objects.filter(post_id=post_id, parent__isnull=True)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)

    def post(self, request, post_id):
        data = request.data.copy()
        data['post'] = post_id
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'post_{post_id}',
                {
                    'type': 'new_comment',
                    'comment': serializer.data
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReplyListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, comment_id):
        replies = Comment.objects.filter(parent_id=comment_id)
        serializer = CommentSerializer(replies, many=True)
        return Response(serializer.data)

    def post(self, request, comment_id):
        data = request.data.copy()
        data['parent'] = comment_id
        data['post'] = Comment.objects.get(id=comment_id).post.id
        serializer = CommentSerializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'post_{data["post"]}',
                {
                    'type': 'new_comment',
                    'comment': serializer.data
                }
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ReactionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, content_type, object_id):
        reaction_type = request.data.get('reaction_type')
        if reaction_type not in ['like', 'heart', 'dislike']:
            return Response({'error': 'Invalid reaction type'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            content_type = ContentType.objects.get(model=content_type)
            content_object = content_type.get_object_for_this_type(id=object_id)
        except (ContentType.DoesNotExist, ValueError):
            return Response({'error': 'Invalid content type or object ID'}, status=status.HTTP_404_NOT_FOUND)
        
        reaction, created = Reaction.objects.get_or_create(
            user=request.user,
            content_type=content_type,
            object_id=object_id,
            reaction_type=reaction_type
        )
        if created:
            channel_layer = get_channel_layer()
            group_name = f'post_{content_object.post.id}' if content_type.model == 'comment' else f'post_{object_id}'
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    'type': 'new_reaction',
                    'reaction': {
                        'id': reaction.id,
                        'user': request.user.email,
                        'reaction_type': reaction_type,
                        'content_type': content_type.model,
                        'object_id': object_id,
                        'timestamp': reaction.created_at.isoformat(),
                    }
                }
            )
            return Response({'message': 'Reaction added'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Reaction already exists'}, status=status.HTTP_200_OK)

class PostApprovalView(APIView):
    permission_classes = [IsAdminOrSuperAdmin]

    def get(self, request):
        posts = Post.objects.filter(is_approved=False)
        serializer = PostSerializer(posts, many=True)
        return Response(serializer.data)

    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id, is_approved=False)
            post.is_approved = True
            post.save()
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'user_{post.user.id}',
                {'type': 'notification', 'message': 'Your post has been approved.'}
            )
            return Response({'message': 'Post approved'}, status=status.HTTP_200_OK)
        except Post.DoesNotExist:
            return Response({'error': 'Post not found or already approved'}, status=status.HTTP_404_NOT_FOUND)