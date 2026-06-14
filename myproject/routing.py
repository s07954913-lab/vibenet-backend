from django.urls import re_path
from activity import consumers

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$',        consumers.ChatConsumer.as_asgi()),
    re_path(r'ws/comments/(?P<post_id>\d+)/$',      consumers.CommentConsumer.as_asgi()),
    re_path(r'ws/notifications/(?P<user_id>[\w-]+)/$', consumers.NotificationConsumer.as_asgi()),
    re_path(r'ws/api-logs/$',                        consumers.APILogConsumer.as_asgi()),
]