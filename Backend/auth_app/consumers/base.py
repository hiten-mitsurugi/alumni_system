# Shared imports and base configurations for all consumer mixins
import json
import logging
import asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from ..status_cache import UserStatusCache

# Configure logger
logger = logging.getLogger(__name__)