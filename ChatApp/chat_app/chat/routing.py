from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Chat consumer with username parameter
    re_path(
        r'^ws/chat/(?P<username>[^/]+)/?$',  # Handles with or without trailing slash
        consumers.ChatConsumer.as_asgi(),
        name='chat_ws'
    ),

    # Optional: Add notification consumer if needed
    # re_path(r'^ws/notifications/$', consumers.NotificationConsumer.as_asgi()),
]