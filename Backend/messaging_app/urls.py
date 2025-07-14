from django.urls import path
from .views import (
    MessageListView, GroupChatCreateView, GroupChatManageView, GroupChatListView,
    ConversationUsersView, MessageRequestView, BlockUserView, MuteConversationView,
    SearchUsersView, PinMessageView
)

urlpatterns = [
    path('private/<int:receiver_id>/', MessageListView.as_view(), name='private_messages'),
    path('group/<int:group_id>/', MessageListView.as_view(), name='group_messages'),
    path('group/', GroupChatListView.as_view(), name='group_list'),
    path('group/create/', GroupChatCreateView.as_view(), name='group_create'),
    path('group/<int:group_id>/manage/', GroupChatManageView.as_view(), name='group_manage'),
    path('conversations/users/', ConversationUsersView.as_view(), name='conversation_users'),
    path('requests/', MessageRequestView.as_view(), name='message_requests'),
    path('block/', BlockUserView.as_view(), name='block_user'),
    path('block/<int:user_id>/', BlockUserView.as_view(), name='unblock_user'),
    path('mute/', MuteConversationView.as_view(), name='mute_conversation'),
    path('search/', SearchUsersView.as_view(), name='search_users'),
    path('pin/<int:message_id>/', PinMessageView.as_view(), name='pin_message'),
]