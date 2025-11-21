import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter

# Set the DJANGO_SETTINGS_MODULE and initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

# Import routing modules after settings are configured
import auth_app.routing
import posts_app.routing
import messaging_app.routing
import notifications_app.routing
from auth_app.middleware import JwtAuthMiddlewareStack

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': JwtAuthMiddlewareStack(
        URLRouter(
            auth_app.routing.websocket_urlpatterns +
            posts_app.routing.websocket_urlpatterns +
            messaging_app.routing.websocket_urlpatterns +
            notifications_app.routing.websocket_urlpatterns
        )
    )
})