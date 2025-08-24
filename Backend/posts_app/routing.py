from django.urls import re_path
from .consumers import PostConsumer, PostsConsumer, PostDetailConsumer

websocket_urlpatterns = [
    # Main posts feed WebSocket for real-time updates
    re_path(r'^ws/posts/feed/$', PostsConsumer.as_asgi()),
    
    # Individual post WebSocket for detailed interactions
    re_path(r'^ws/posts/(?P<post_id>\d+)/$', PostDetailConsumer.as_asgi()),
    
    # Legacy route for backward compatibility
    re_path(r'^ws/post/(?P<post_id>\d+)/$', PostConsumer.as_asgi()),
]