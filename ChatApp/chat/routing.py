from django.urls import re_path
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<sender>\w+)/(?P<recipient>\w+)/$', ChatConsumer.as_asgi()),
]
