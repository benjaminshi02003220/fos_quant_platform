# wslog/routing.py
from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
        url(r'^ws/log/duiqiao/$', consumers.DuiqiaoLogConsumer),
        url(r'^ws/log/limitbuy/$', consumers.LimitbuyLogConsumer),
    ]