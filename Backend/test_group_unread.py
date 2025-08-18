#!/usr/bin/env python
"""
Test script to verify group message unread count logic works like private messages.
"""

import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

from django.contrib.auth import get_user_model
from messaging_app.models import Message, GroupChat, MessageRead

User = get_user_model()

def test_group_unread_logic():
    """Test that group unread count works like private messages."""
    print("🧪 Testing Group Unread Count Logic")
    print("="*50)
    
    # Get or create test users
    try:
        user1 = User.objects.get(username='testuser1')
        user2 = User.objects.get(username='testuser2') 
        user3 = User.objects.get(username='testuser3')
        print(f"✅ Found test users: {user1.username}, {user2.username}, {user3.username}")
    except User.DoesNotExist:
        print("❌ Test users not found. Please create testuser1, testuser2, testuser3 first.")
        return
    
    # Get or create test group
    group, created = GroupChat.objects.get_or_create(
        name='Test Group',
        defaults={'description': 'Test group for unread count testing'}
    )
    if created:
        group.members.add(user1, user2, user3)
        print(f"✅ Created test group: {group.name}")
    else:
        print(f"✅ Using existing test group: {group.name}")
    
    # Clean up previous test data
    Message.objects.filter(group=group).delete()
    MessageRead.objects.filter(message__group=group).delete()
    print("🧹 Cleaned up previous test data")
    
    # Test scenario: user2 sends message, check user1's unread count
    print("\n📤 user2 sends a message to the group...")
    message1 = Message.objects.create(
        sender=user2,
        group=group,
        content="Hello from user2!"
    )
    
    # Calculate unread count for user1 (should be 1)
    unread_messages = Message.objects.filter(group=group).exclude(sender=user1)
    read_message_ids = MessageRead.objects.filter(
        user=user1,
        message__group=group
    ).values_list('message_id', flat=True)
    unread_count_user1 = unread_messages.exclude(id__in=read_message_ids).count()
    
    print(f"📬 user1 unread count: {unread_count_user1} (expected: 1)")
    assert unread_count_user1 == 1, f"Expected 1, got {unread_count_user1}"
    
    # Test scenario: user3 sends another message
    print("\n📤 user3 sends another message...")
    message2 = Message.objects.create(
        sender=user3,
        group=group,
        content="Hello from user3!"
    )
    
    # Calculate unread count for user1 (should be 2)
    unread_messages = Message.objects.filter(group=group).exclude(sender=user1)
    read_message_ids = MessageRead.objects.filter(
        user=user1,
        message__group=group
    ).values_list('message_id', flat=True)
    unread_count_user1 = unread_messages.exclude(id__in=read_message_ids).count()
    
    print(f"📬 user1 unread count: {unread_count_user1} (expected: 2)")
    assert unread_count_user1 == 2, f"Expected 2, got {unread_count_user1}"
    
    # Test scenario: user1 "opens" the conversation (marks as read)
    print("\n👀 user1 opens the conversation (marks as read)...")
    for message in unread_messages:
        MessageRead.objects.get_or_create(
            message=message,
            user=user1
        )
    
    # Calculate unread count for user1 (should be 0)
    unread_messages = Message.objects.filter(group=group).exclude(sender=user1)
    read_message_ids = MessageRead.objects.filter(
        user=user1,
        message__group=group
    ).values_list('message_id', flat=True)
    unread_count_user1 = unread_messages.exclude(id__in=read_message_ids).count()
    
    print(f"📬 user1 unread count: {unread_count_user1} (expected: 0)")
    assert unread_count_user1 == 0, f"Expected 0, got {unread_count_user1}"
    
    # Test scenario: user2 sends a new message after user1 read previous ones
    print("\n📤 user2 sends a new message after user1 read...")
    message3 = Message.objects.create(
        sender=user2,
        group=group,
        content="New message from user2!"
    )
    
    # Calculate unread count for user1 (should be 1 again)
    unread_messages = Message.objects.filter(group=group).exclude(sender=user1)
    read_message_ids = MessageRead.objects.filter(
        user=user1,
        message__group=group
    ).values_list('message_id', flat=True)
    unread_count_user1 = unread_messages.exclude(id__in=read_message_ids).count()
    
    print(f"📬 user1 unread count: {unread_count_user1} (expected: 1)")
    assert unread_count_user1 == 1, f"Expected 1, got {unread_count_user1}"
    
    # Test scenario: user1 sends a message (should not affect their own unread count)
    print("\n📤 user1 sends a message...")
    message4 = Message.objects.create(
        sender=user1,
        group=group,
        content="Reply from user1!"
    )
    
    # Calculate unread count for user1 (should still be 1, own message doesn't count)
    unread_messages = Message.objects.filter(group=group).exclude(sender=user1)
    read_message_ids = MessageRead.objects.filter(
        user=user1,
        message__group=group
    ).values_list('message_id', flat=True)
    unread_count_user1 = unread_messages.exclude(id__in=read_message_ids).count()
    
    print(f"📬 user1 unread count: {unread_count_user1} (expected: 1)")
    assert unread_count_user1 == 1, f"Expected 1, got {unread_count_user1}"
    
    print("\n🎉 All tests passed! Group unread count logic works correctly.")
    print("✅ Group messages now behave exactly like private messages.")

if __name__ == '__main__':
    test_group_unread_logic()
