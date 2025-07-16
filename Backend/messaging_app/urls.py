from django.urls import path
from .views import (
    SearchView, ConversationListView, MessageListView, SendMessageView,
    GroupChatCreateView, GroupChatManageView, GroupChatListView,
    ConversationUsersView, MessageRequestView, BlockUserView,
    MuteConversationView, PinMessageView, UploadView
)

urlpatterns = [
    path('search/', SearchView.as_view(), name='search'),  # ✅ only one search endpoint
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/users/', ConversationUsersView.as_view(), name='conversation_users'),
    
    path('private/<uuid:receiver_id>/', MessageListView.as_view(), name='private_messages_uuid'),
    path('private/<int:receiver_id>/', MessageListView.as_view(), name='private_messages_int'),
    path('group/<uuid:group_id>/', MessageListView.as_view(), name='group_messages'),
    
    path('send/', SendMessageView.as_view(), name='send_message'),
    
    path('group/create/', GroupChatCreateView.as_view(), name='group_create'),
    path('group/<uuid:group_id>/manage/', GroupChatManageView.as_view(), name='group_manage'),
    path('group/', GroupChatListView.as_view(), name='group_list'),

    path('requests/', MessageRequestView.as_view(), name='message_requests'),
    
    path('block/', BlockUserView.as_view(), name='block_user'),
    path('block/<uuid:user_id>/', BlockUserView.as_view(), name='unblock_user'),
    
    path('mute/', MuteConversationView.as_view(), name='mute_conversation'),
    
    path('pin/<uuid:message_id>/', PinMessageView.as_view(), name='pin_message'),
    path('upload/', UploadView.as_view(), name='upload_attachment'),
]
