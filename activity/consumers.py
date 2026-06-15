import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name  = self.scope['url_route']['kwargs']['room_name']
        self.group_name = f'chat_{self.room_name}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(self.group_name, {
            'type':        'chat_message',
            'text':        data.get('text', ''),
            'sender_id':   data.get('sender_id', ''),
            'sender_name': data.get('sender_name', ''),
        })

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'text':        event.get('text', ''),
            'sender_id':   event.get('sender_id', ''),
            'sender_name': event.get('sender_name', ''),
        }))


class CommentConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.post_id    = self.scope['url_route']['kwargs']['post_id']
        self.group_name = f'comments_{self.post_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        await self.channel_layer.group_send(self.group_name, {
            'type':      'new_comment',
            'text':      data.get('text', ''),
            'user_name': data.get('user_name', ''),
            'user_id':   data.get('user_id', ''),
        })

    async def new_comment(self, event):
        await self.send(text_data=json.dumps(event))


class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id    = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'notifications_{self.user_id}'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def send_notification(self, event):
        await self.send(text_data=json.dumps({
            'type':    event.get('notif_type', ''),
            'message': event.get('message', ''),
            'sender':  event.get('sender', ''),
        }))


class APILogConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.group_name = 'api_logs'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data):
        pass

    async def new_log(self, event):
        await self.send(text_data=json.dumps(event))