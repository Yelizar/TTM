from django.conf.urls import url

import website.session.consumer
websocket_urlpatterns = [
    url(r'^ws/session-initialization/(?P<session_name>[^/]+)/$', website.session.consumer.SessionConsumer),
]

