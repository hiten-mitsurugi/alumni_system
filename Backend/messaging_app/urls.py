from django.urls import path
from .views import (
    SearchView, ConversationListView, MessageListView, SendMessageView,
    GroupChatCreateView, GroupChatManageView, GroupChatListView, GroupMembersView,
    ConversationUsersView, MessageRequestView, BlockUserView,
    PinMessageView, BumpMessageView, UploadView,
    GroupMemberRequestView, GroupMemberRequestManageView, ForwardMessageView,
    MessageSearchView
)

urlpatterns = [
    path('search/', SearchView.as_view(), name='search'),  # ✅ only one search endpoint
    path('search/messages/', MessageSearchView.as_view(), name='search_messages'),
    path('conversations/', ConversationListView.as_view(), name='conversation_list'),
    path('conversations/users/', ConversationUsersView.as_view(), name='conversation_users'),
    
    path('private/<int:receiver_id>/', MessageListView.as_view(), name='private_messages_int'),
    path('private/<uuid:receiver_id>/', MessageListView.as_view(), name='private_messages_uuid'),
    path('group/<uuid:group_id>/', MessageListView.as_view(), name='group_messages'),
    
    path('send/', SendMessageView.as_view(), name='send_message'),
    
    path('group/create/', GroupChatCreateView.as_view(), name='group_create'),
    path('group/<uuid:group_id>/manage/', GroupChatManageView.as_view(), name='group_manage'),
    path('group/<uuid:group_id>/members/', GroupMembersView.as_view(), name='group_members'),
    path('group/<uuid:group_id>/member-requests/', GroupMemberRequestView.as_view(), name='group_member_requests'),
    path('member-request/<uuid:request_id>/manage/', GroupMemberRequestManageView.as_view(), name='manage_member_request'),
    path('group/', GroupChatListView.as_view(), name='group_list'),

    path('requests/', MessageRequestView.as_view(), name='message_requests'),
    
    path('block/', BlockUserView.as_view(), name='block_user'),
    path('block/<int:user_id>/', BlockUserView.as_view(), name='unblock_user'),
    
    path('pin/<uuid:message_id>/', PinMessageView.as_view(), name='pin_message'),
    path('bump/<uuid:message_id>/', BumpMessageView.as_view(), name='bump_message'),
    path('forward/', ForwardMessageView.as_view(), name='forward_message'),
    path('upload/', UploadView.as_view(), name='upload_attachment'),
]
