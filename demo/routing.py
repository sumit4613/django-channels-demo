from django.urls import path

from .consumers import MyConsumer

websocket_urlpatterns = [
    path("ws/user/notifications/", MyConsumer.as_asgi()),
]
