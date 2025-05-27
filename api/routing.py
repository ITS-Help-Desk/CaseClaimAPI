from django.urls import re_path
from api.consumers import Consumer

websocket_urlpatterns = [
    re_path(r'ws/caseflow/$', Consumer.as_asgi()),
]
