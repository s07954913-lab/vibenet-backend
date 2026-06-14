from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification

def send_notification(recipient_id, sender_username, notif_type, message):
    # DB mein save karo
    Notification.objects.create(
        user_id   = recipient_id,
        from_name = sender_username,
        type      = notif_type,
    )
    # Live push karo
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        f'notifications_{recipient_id}',
        {
            'type':       'send_notification',
            'notif_type': notif_type,
            'message':    message,
            'sender':     sender_username,
        }
    )