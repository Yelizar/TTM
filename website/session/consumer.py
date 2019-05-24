from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer
from api.serializers import UserSerializer
from channels.db import database_sync_to_async
import json
from .models import ChannelRoom


class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_name = self.scope['url_route']['kwargs']['session_name']
        self.room_group_name = 'session_%s' % self.session_name
        self.user = self.scope['user']
        self.channelRoom = await self.get_channel_room()
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        user = UserSerializer(self.scope['user'])
        if user.data['role'] == 'Student':
            await self.send(text_data=json.dumps({
                'student': user.data
            }))
        elif user.data['role'] == 'Tutor':
            if await self.add_to_channel_room():
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'add_user',
                        'user': user.data
                    }
                )
            else:
                await self.disconnect(483)

    async def disconnect(self, close_code):
        # Leave session
        await self.remove_from_channel_room()
        await  self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if 'new_user' in text_data_json.keys():
            user = UserSerializer(self.scope['user'])
            print(user.data)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': user.data
                }
            )

    async def add_user(self, event):
        user = event['user']
        await self.send(text_data=json.dumps({
            'tutor': user
        }))

    @database_sync_to_async
    def get_channel_room(self):
        return ChannelRoom.objects.get_or_new(self.session_name)[0]

    @database_sync_to_async
    def add_to_channel_room(self):
        return ChannelRoom.objects.add_visitor(self.user.username, self.channelRoom)

    @database_sync_to_async
    def remove_from_channel_room(self):
        return ChannelRoom.objects.remove_visitor(self.user.username, self.channelRoom)



