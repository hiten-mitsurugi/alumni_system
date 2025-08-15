"""
JWT Authentication Middleware for WebSocket connections
"""
import logging
from urllib.parse import parse_qs
from django.contrib.auth.models import AnonymousUser
from django.contrib.auth import get_user_model
from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import TokenError

User = get_user_model()
logger = logging.getLogger(__name__)

@database_sync_to_async
def get_user_from_token(token_string):
    """
    Get user from JWT token string
    """
    try:
        # Validate the token
        token = AccessToken(token_string)
        user_id = token['user_id']
        
        # Get the user
        user = User.objects.get(id=user_id)
        logger.info(f"WebSocket JWT auth successful for user: {user.username} (ID: {user.id})")
        return user
        
    except TokenError as e:
        logger.warning(f"WebSocket JWT token error: {str(e)}")
        return AnonymousUser()
    except User.DoesNotExist:
        logger.warning(f"WebSocket JWT: User not found for token")
        return AnonymousUser()
    except Exception as e:
        logger.error(f"WebSocket JWT auth unexpected error: {str(e)}")
        return AnonymousUser()

class JwtAuthMiddleware(BaseMiddleware):
    """
    JWT authentication middleware for WebSocket connections.
    
    Expects the JWT token to be passed as a query parameter: ?token=<jwt_token>
    """
    
    async def __call__(self, scope, receive, send):
        # Extract token from query string
        query_string = scope.get('query_string', b'').decode('utf-8')
        query_params = parse_qs(query_string)
        token = query_params.get('token', [None])[0]
        
        if token:
            # Authenticate user with JWT token
            scope['user'] = await get_user_from_token(token)
            logger.info(f"WebSocket connection authenticated user: {scope['user']}")
        else:
            # No token provided - use anonymous user
            scope['user'] = AnonymousUser()
            logger.warning("WebSocket connection: No token provided, using anonymous user")
        
        return await super().__call__(scope, receive, send)

def JwtAuthMiddlewareStack(inner):
    """
    Convenience function to apply JWT authentication middleware
    """
    return JwtAuthMiddleware(inner)
