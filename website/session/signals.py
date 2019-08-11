
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils.html import format_html
from notifications.signals import notify

from tplatform.views import notice_tutors
from website.session.models import Session, Account


def get_absolute_connect_url(pk):
    return reverse('session:connect', kwargs={'pk': pk})


@receiver(post_save, sender=Session)
def session_initialized(instance, created, **kwargs):
    """
    Send notification to tutors who is searching a session
    """
    if created:
        notice_tutors(instance)
        student = instance.student
        tutor_list = get_user_model().objects.filter(account__notice=True, account__native_language=instance.language)
        verb = format_html("<a href='{url}'>Connect to student</a>".format(url=get_absolute_connect_url(student.id)))
        notify.send(sender=student,
                    recipient=tutor_list,
                    verb=verb,
                    description='When student initialize a session. List of tutors receive a notification'
                                'about new session')


@receiver(post_save, sender=Account)
def applicant(instance, created, **kwargs):
    """
    Send notification to admin when tutor is applied
    """
    if not created:
        subject = 'New Tutor'
        message = 'Hi Admin, {name} applied as a tutor. Email of user - {email}'.format(name=instance.website.first_name,
                                                                                    email=instance.website.email)
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [settings.EMAIL_FOR_NOTIFICATION]
        send_mail(subject, message, email_from, recipient_list)
