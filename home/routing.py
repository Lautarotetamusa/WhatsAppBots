from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r'new_bot/$', consumers.CreateBotConsumer.as_asgi()),
]
