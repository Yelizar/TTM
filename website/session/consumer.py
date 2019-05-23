from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from api.serializers import UserSerializer
import json


class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_name = self.scope['url_route']['kwargs']['session_name']
        self.room_group_name = 'session_%s' % self.session_name

        user = UserSerializer(self.scope['user'])

        if user.data['role'] == 'Tutor':
            self.scope['session']['tutor'] = user.data['username']
        # Join session
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        await self.send(text_data=json.dumps({'user': user.data}))

    async def disconnect(self, close_code):
        # Leave session
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        self.groups.append(text_data_json['student'])
        print(self.groups)
        if 'student' in text_data_json.keys():
            student = text_data_json['student']
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'add_student',
                    'student': student
                },
            )

    async def add_student(self, event):
        student = event['student']

        # Sendnto WebSocket
        await self.send(text_data=json.dumps({
            'student': student
        }))

