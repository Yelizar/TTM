from website.access.models import Account
from django.db import models
from django.db.models import Q
from django.db import DataError
from datetime import datetime, timezone
from django.core.exceptions import ObjectDoesNotExist


class SessionCoinsManager(models.Manager):

    def coins_operation(self, student, tutor, quantity=1):
        student = self.get(user=student)
        tutor = self.get(user=tutor)
        try:
            student.coins -= quantity
            tutor.coins += quantity
            student.save()
            tutor.save()
            return True
        except DataError:
            return False


class SessionManager(models.Manager):

    def active_session(self, current_user):
        obj_set = self.filter(Q(student_id=current_user.id, is_active=True)
                              | Q(tutor_id=current_user.id, tutor_confirm=None))
        if obj_set:
            return obj_set
        return None

    def get_last_session(self, current_user):
        obj_set = self.filter(Q(student_id=current_user.id, is_going=True, student_confirm=None)
                        | Q(tutor_id=current_user.id, tutor_confirm=None))
        if obj_set:
            return obj_set.first()
        return None

    def get_history(self, current_user):
        obj_set = self.filter(Q(student_id=current_user.id)
                        | Q(tutor_id=current_user.id))
        return obj_set

    def get_create_timeout(self, current_user, language):
        try:
            obj = self.get(student=current_user, language=language, is_active=True)
            return obj, None
        except ObjectDoesNotExist:
            obj_set = self.filter(student=current_user)
            if obj_set.exists():
                obj = obj_set.last()
                timeout = datetime.now(timezone.utc) - obj.updated
                if timeout.total_seconds() < 10:
                    return obj, (10 - int(timeout.total_seconds()))
            obj = self.create(student=current_user, language=language, is_active=True)
            return obj, True





