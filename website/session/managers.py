from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import Q
from django.db import DataError


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
        obj = self.filter(id=room.id, is_active=True)
        if obj:
            for o in obj:
                o.delete()
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
                o.delete()
                return True
        return False


class SessionCoinsManager(models.Manager):

    def coin_operations(self, user_id, operation=None, quantity=1):
        obj = self.get(user_id=user_id)
        if obj:
            try:
                if operation == "add":
                    obj.coins += quantity
                if operation == "remove":
                    obj.coins -= quantity
                obj.save()
                return True
            except DataError:
                return False
        return False


class SessionManager(models.Manager):

    def active_session(self, current_user):
        obj_set = self.filter(Q(student_id=current_user.id, is_active=True)
                              | Q(tutor_id=current_user.id, tutor_confirm=False))
        if obj_set:
            return obj_set.first()
        return None

    def get_last_session(self, current_user):
        obj_set = self.filter(Q(student_id=current_user.id, is_going=True, student_confirm=False)
                        | Q(tutor_id=current_user.id, tutor_confirm=False))
        if obj_set:
            return obj_set.first()
        return None

    def get_history(self, current_user):
        obj_set = self.filter(Q(student_id=current_user.id)
                        | Q(tutor_id=current_user.id))
        return obj_set

