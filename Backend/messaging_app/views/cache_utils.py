"""
Cache utility functions for messaging app.
Handles invalidation of conversation and unread count caches.
"""

import logging
from django.core.cache import cache

logger = logging.getLogger(__name__)


def invalidate_unread_counts_cache(user_id):
    """Invalidate unread counts cache for a specific user"""
    cache_key = f"unread_counts_{user_id}"
    cache.delete(cache_key)
    logger.info(f"🚀 Cache INVALIDATED: Unread counts cache for user {user_id}")


def invalidate_unread_counts_for_users(user_ids):
    """Invalidate unread counts cache for multiple users"""
    for user_id in user_ids:
        invalidate_unread_counts_cache(user_id)
