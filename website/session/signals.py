from .models import ChannelRoom
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from notifications.signals import notify
from website.access.models import CustomUser

@receiver(post_save, sender=ChannelRoom)
def session_initialized(sender, instance, created, using, **kwargs):
    """
    Send notification to a list of tutors who is searching a session
    """
    if created:
        tutor_list = CustomUser.objects.tutor_list()
        url = instance.get_absolute_url()
        verb = '<a href="{}">Room</a>'.format(url)
        notify.send(sender=instance.student, recipient=tutor_list, verb='New session\n' + verb, description='URL',)