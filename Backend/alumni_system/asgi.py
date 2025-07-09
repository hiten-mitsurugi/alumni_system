import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Set the DJANGO_SETTINGS_MODULE and initialize Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alumni_system.settings')
django.setup()

# Import routing modules after settings are configured
import auth_app.routing
import posts_app.routing
import messaging_app.routing

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(
            auth_app.routing.websocket_urlpatterns +
            posts_app.routing.websocket_urlpatterns +
            messaging_app.routing.websocket_urlpatterns
        )
    )
})