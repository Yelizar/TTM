
from django.conf import settings
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import reverse
from django.utils.html import format_html

from tplatform.views import notice_tutors_telegram
from website.session.models import Session, Notifications
from website.access.models import Account


def get_absolute_connect_url(pk):
    return reverse('session:connect', kwargs={'pk': pk})


@receiver(post_save, sender=Session)
def session_initialized(instance, created, **kwargs):
    """
    Send notification to tutors who is searching a session
    """
    student = instance.student
    tutor_list = Account.objects.filter(notice=True, native_language=instance.language).exclude(id=student.id)
    if created:
        message = format_html("<a href='{url}'>Connect to student</a>".format(url=get_absolute_connect_url(student.id)))
        for tutor in tutor_list:
            Notifications.objects.create(sender=student, recipient=tutor, session=instance, message=message)
    elif not created:
        if instance.is_active is False and instance.tutor is None:
            verb = 'Session {} has been canceled cancelled'.format(student)
            notice_set = Notifications.objects.filter(session=instance)
            for notice in notice_set:
                notice.mark_as_read()
    notice_tutors_telegram(instance, created)


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
