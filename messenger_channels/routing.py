from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/message/', consumers.MessengerConsumer.as_asgi()),
]
