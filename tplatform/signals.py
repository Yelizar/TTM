# from .models import TelegramSession
# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .views import notice_tutors


# @receiver(post_save, sender=TelegramSession)
# def session_initialized(instance, created, **kwargs):
#     """
#     Send notification to tutors who is searching a session
#     """
#     if created:
#         notice_tutors(instance)
