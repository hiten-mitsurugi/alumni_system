# This file imports all consumers from individual files
# Maintaining backward compatibility for existing imports

from .posts_consumer import PostsConsumer
from .post_detail_consumer import PostDetailConsumer
from .post_consumer import PostConsumer

__all__ = [
    'PostsConsumer',
    'PostDetailConsumer',
    'PostConsumer',
]