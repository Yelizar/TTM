from django.db import models
from django.db.models import Q


class TelegramSessionManager(models.Manager):

    def get_last_session(self, current_user):
        obj_set = self.filter(Q(student_id=current_user.id, is_active=True)
                        | Q(tutor_id=current_user.id, is_active=True))
        if obj_set:
            return obj_set.first()
        return None

    def get_history(self, current_user):
        obj_set = self.filter(Q(student_id=current_user.id)
                        | Q(tutor_id=current_user.id))
        return obj_set