# This file now imports all consumers from the consumers/ directory
# Maintaining backward compatibility for existing imports

from .consumers.posts_consumer import PostsConsumer
from .consumers.post_detail_consumer import PostDetailConsumer
from .consumers.post_consumer import PostConsumer

__all__ = [
    'PostsConsumer',
    'PostDetailConsumer',
    'PostConsumer',
]
