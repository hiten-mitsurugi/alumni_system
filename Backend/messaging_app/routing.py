from django.urls import path
from .consumers import PrivateChatConsumer, GroupChatConsumer

websocket_urlpatterns = [
    path('ws/private/', PrivateChatConsumer.as_asgi()),
    path('ws/group/<uuid:group_id>/', GroupChatConsumer.as_asgi()),
]