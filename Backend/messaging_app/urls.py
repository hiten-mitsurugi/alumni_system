from django.urls import path
from .views import MessageListView, GroupChatCreateView, GroupChatManageView

urlpatterns = [
    path('messages/private/<int:receiver_id>/', MessageListView.as_view(), name='private_messages'),
    path('messages/group/<int:group_id>/', MessageListView.as_view(), name='group_messages'),
    path('group/create/', GroupChatCreateView.as_view(), name='group_create'),
    path('group/<int:group_id>/manage/', GroupChatManageView.as_view(), name='group_manage'),
]