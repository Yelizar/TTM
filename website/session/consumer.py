from channels.generic.websocket import AsyncWebsocketConsumer
from api.serializers import UserSerializer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json
from .models import ChannelRoom, ChannelNames


class SessionConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_name = self.scope['url_route']['kwargs']['session_name']
        self.room_group_name = 'session_%s' % self.session_name
        self.user = await self.get_serialized_user()
        self.channelRoom = await self.get_channel_room()
        await self.set_channel_name()
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        if self.user.data['role'] == 'Tutor':
            if await self.add_to_channel_room():
                await self.send_message('add_user',
                                        self.user.data)
            else:
                await self.disconnect(483)

    async def disconnect(self, close_code, remove_user=None, channel_name=None):
        if remove_user is None:
            remove_user = self.user
        if channel_name is None:
            channel_name = self.channel_name
        # Leave session
        await self.remove_from_channel_room()
        await self.disable_channel_name(remove_user.data['id'])
        await self.send_message('remove_user',
                                remove_user.data)
        # change self.channel_name when remove a user
        await  self.channel_layer.group_discard(
            self.room_group_name,
            channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if 'chosenTutor' in text_data_json.keys():
            user = await self.get_serialized_user(text_data_json['chosenTutor'])
            for t in self.channelRoom.tutor.all():
                if t.username != user.data['username']:
                    remove_user = await self.get_serialized_user(t)
                    channel_obj = await self.get_channel_name(remove_user.data['id'])
                    await self.disconnect(close_code=400, remove_user=remove_user,
                                          channel_name=channel_obj.channel_name)
            #         add self.channel_name to each user in ChannelRoom DB
            await self.send_message('start_session',
                                    user.data)
            await self.close_room()

    async def start_session(self, event):
        user = event['message']
        await self.send(text_data=json.dumps({
            'start_session': user
        }))

    async def add_user(self, event):
        user = event['message']
        await self.send(text_data=json.dumps({
            'add_user': user
        }))

    async def remove_user(self, event):
        user = event['message']
        await self.send(text_data=json.dumps({
            'remove_user': user
        }))

    async def get_serialized_user(self, name=None):
        if name is None:
            obj = self.scope['user']
        else:
            obj = await self.get_user_obj(name)
        return UserSerializer(obj)

    async def send_message(self, definition, message):
        pre_dict = dict()
        pre_dict['type'] = definition
        pre_dict['message'] = message
        await self.channel_layer.group_send(self.room_group_name, pre_dict)

    @database_sync_to_async
    def get_user_obj(self, username):
        """Get User Object <CustomUserModel>"""
        return get_user_model().objects.get(username=username)

    @database_sync_to_async
    def get_channel_room(self):
        """Get Room object <ChannelRoomModel>. Collection users in channel."""
        return ChannelRoom.objects.get_or_new(self.session_name)[0]

    @database_sync_to_async
    def add_to_channel_room(self):
        """Add User to Room Object"""
        return ChannelRoom.objects.add_visitor(self.user.data['username'], self.channelRoom)

    @database_sync_to_async
    def remove_from_channel_room(self):
        """Remove User from Room Object"""
        return ChannelRoom.objects.remove_visitor(self.user.data['username'], self.channelRoom)

    @database_sync_to_async
    def close_room(self):
        """Change status ChannelRoom Object.is_active = False"""
        return ChannelRoom.objects.close(self.channelRoom)

    @database_sync_to_async
    def set_channel_name(self):
        """Assigns channel name to specific user. Channel name getting from Redis DB"""
        return ChannelNames.objects.create(channel_id=self.user.data['id'], channel_name=self.channel_name)

    @database_sync_to_async
    def get_channel_name(self, channel_id):
        """Get ChannelName object <ChannelNamesModel>. Connections between users and channels names."""
        return ChannelNames.objects.get_one(channel_id=channel_id)[0]

    @database_sync_to_async
    def disable_channel_name(self, channel_id):
        """Change status ChannelNames Object.is_active = False"""
        return ChannelNames.objects.disable(channel_id=channel_id)
