# This file now imports all models from the models/ directory
# Maintaining backward compatibility for existing imports

from .models.message import Message
from .models.attachment import Attachment
from .models.group_chat import GroupChat
from .models.message_request import MessageRequest
from .models.blocked_user import BlockedUser
from .models.message_reaction import MessageReaction
from .models.link_preview import LinkPreview
from .models.group_member_request import GroupMemberRequest
from .models.message_read import MessageRead
from .models.message_mention import MessageMention

__all__ = [
    'Message',
    'Attachment',
    'GroupChat',
    'MessageRequest',
    'BlockedUser',
    'MessageReaction',
    'LinkPreview',
    'GroupMemberRequest',
    'MessageRead',
    'MessageMention',
]
