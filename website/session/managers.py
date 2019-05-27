from django.contrib.auth import get_user_model
from django.db import models


class ChannelRoomManager(models.Manager):
    """
    Managers methods for consumer.
    """

    def get_or_new(self, username):
        user = get_user_model().objects.get(username=username)
        if user.role == 'Student':
            room = self.filter(student__username=user.username, is_active=True)
            if room:
                return room.first(), False
            else:
                obj = self.model(student=user, is_active=True)
                obj.save()
                return obj, True
        return None, False

    def add_visitor(self, username, room):
        user = get_user_model().objects.get(username=username)
        if user.role == 'Tutor':
            obj = self.get(id=room.id)
            if obj:
                obj.tutor.add(user)
                obj.save()
                return True

        return False

    def remove_visitor(self, username, room):
        user = get_user_model().objects.get(username=username)
        if user.role == 'Tutor':
            obj = self.get(id=room.id)
            if obj:
                obj.tutor.remove(user)
                obj.save()
                return True

        return False

    def close(self, room):
        obj = self.get(id=room.id)
        if obj:
            obj.is_active = False
            obj.save()
            return True
        return False


class ChannelNamesManager(models.Manager):
    """
    Managers methods for consumer.
    """

    def get_one(self, channel_id):
        obj = self.filter(channel_id=channel_id, is_active=True)
        if obj:
            return obj.first(), False
        return False

    def disable(self, channel_id):
        obj = self.filter(channel_id=channel_id, is_active=True)
        if obj:
            for o in obj:
                o.is_active = False
                o.save()
                return True
        return False
