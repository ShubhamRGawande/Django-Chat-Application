import os
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
import chat.routing

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_app.settings')

# Initialize Django ASGI application
django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    # HTTP requests
    "http": django_asgi_app,

    # WebSocket handler with security layers
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                chat.routing.websocket_urlpatterns
            )
        )
    ),
})