from channels.generic.websocket import AsyncWebsocketConsumer
from api.serializers import UserSerializer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
import json
from .models import ChannelRoom, ChannelNames, Session, SessionCoins
from website.access.models import Account


class SessionConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        # noinspection PyAttributeOutsideInit
        self.session_name = self.scope['url_route']['kwargs']['session_name']
        # noinspection PyAttributeOutsideInit
        self.room_group_name = 'session_%s' % self.session_name
        # noinspection PyAttributeOutsideInit
        self.user = await self.get_serialized_user()
        # noinspection PyAttributeOutsideInit
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
        await self.remove_from_channel_room(username=remove_user.data['username'])
        await self.send_message('remove_user',
                                remove_user.data)
        await  self.channel_layer.group_discard(
            self.room_group_name,
            channel_name
        )
        await self.disable_channel_name(remove_user.data['id'])
        if not self.channelRoom.tutor.exists():
            await self.close_room()
            await self.close()

    # Receive message from WebSocket
    # noinspection PyMethodOverriding
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        if 'chosenTutor' in text_data_json.keys():
            user = await self.get_serialized_user(text_data_json['chosenTutor'])
            for t in self.channelRoom.tutor.all():
                # This loop is getting tutor data(id & channel name) => to disconnect from room
                if t.username != user.data['username']:
                    remove_user = await self.get_serialized_user(t)
                    channel_obj = await self.get_channel_name(remove_user.data['id'])
                    await self.disconnect(close_code=400, remove_user=remove_user,
                                          channel_name=channel_obj.channel_name)
            if await self.take_coin(user_id=self.user.data['id']):
                await self.session_initialization(student_id=self.user.data['id'], tutor_id=user.data['id'], is_going=True)
                tutor_number = await self.get_tutor_number(tutor_id=user.data['id'])
                await self.send_message('start_session',
                                        tutor_number)
            else:
                # test exception
                print("Student don't have enough coins for session ")

    async def start_session(self, event):
        tutor_number = event['message']
        await self.send(text_data=json.dumps({
            'start_session': tutor_number
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
        return Account.objects.get(user__username=username)

    @database_sync_to_async
    def get_channel_room(self):
        """Get Room object <ChannelRoomModel>. Collection users in channel."""
        return ChannelRoom.objects.get_or_new(username=self.session_name)[0]

    @database_sync_to_async
    def add_to_channel_room(self):
        """Add User to Room Object"""
        return ChannelRoom.objects.add_visitor(username=self.user.data['username'], room=self.channelRoom)

    @database_sync_to_async
    def remove_from_channel_room(self, username):
        """Remove User from Room Object"""
        return ChannelRoom.objects.remove_visitor(username=username, room=self.channelRoom)

    @database_sync_to_async
    def close_room(self):
        """Delete ChannelRoom Object.delete()"""
        return ChannelRoom.objects.close(room=self.channelRoom)

    @database_sync_to_async
    def set_channel_name(self):
        """Assigns channel name to specific user. Channel name getting from Redis DB"""
        return ChannelNames.objects.get_or_create(channel_id=self.user.data['id'], channel_name=self.channel_name)

    @database_sync_to_async
    def get_channel_name(self, channel_id):
        """Get ChannelName object <ChannelNamesModel>. Connections between users and channels names."""
        return ChannelNames.objects.get_one(channel_id=channel_id)[0]

    @database_sync_to_async
    def disable_channel_name(self, channel_id):
        """Delete ChannelNames Object.delete()"""
        return ChannelNames.objects.disable(channel_id=channel_id)

    # @database_sync_to_async
    # def get_tutor_number(self, tutor_id, com_method='Appear'):
    #     """Get Number or URl to contact tutor Object.get()"""
    #     return CommunicationMethodNumber.objects.get_number(user_id=tutor_id, communication_method=com_method)[0]

    @database_sync_to_async
    def take_coin(self, user_id):
        """Change quantity of session coins Object.coins -= quantity <SessionCoins>"""
        return SessionCoins.objects.coin_operations(user_id=user_id, operation='remove', quantity=1)

    @database_sync_to_async
    def session_initialization(self, student_id, tutor_id, is_going=True, communication_method=4, language=1):
        """Session initializer. Create Session Object.create()"""
        return Session.objects.create(student_id=student_id, tutor_id=tutor_id, session_coin=1, language_id=language,
                                      communication_method_id=communication_method, is_going=is_going)
