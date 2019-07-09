from django.db import models
from .managers import *

# Create your models here.


def tutor_directory_path(instance, filename):
    return 'website/tutors/chat_id-{0}_{1}/cv/{2}'.format(instance.chat_id, instance.name, filename)


class TelegramUser(models.Model):
    chat_id = models.CharField(max_length=64)
    username = models.CharField(max_length=128, blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    chat_type = models.CharField(max_length=64, blank=True, null=True)
    native_language = models.CharField(max_length=64, blank=True, null=True)
    learning_language = models.CharField(max_length=64, blank=True, null=True)
    appear = models.CharField(max_length=64, blank=True, null=True)
    notice = models.BooleanField(default=False)
    phone = models.CharField(max_length=17, blank=True, null=True)
    dob = models.DateField('Date of birthday', auto_now=False, auto_now_add=False, blank=True, null=True)
    cv = models.FileField(upload_to=tutor_directory_path, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return '{}'.format(self.name)


class TelegramSession(models.Model):
    student = models.ForeignKey(TelegramUser, related_name='Student',
                                on_delete=models.CASCADE,)
    tutor = models.ForeignKey(TelegramUser, related_name="Tutor",
                              on_delete=models.CASCADE, blank=True, null=True)
    language = models.CharField(max_length=64, blank=True, null=True)

    student_confirm = models.BooleanField(default=False)
    tutor_confirm = models.BooleanField(default=False)
    is_going = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rate = models.PositiveSmallIntegerField("Session Rate", help_text='Default 5 starts', default=5)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    objects = TelegramSessionManager()

    class Meta:
        verbose_name = 'TelegramSession'
        verbose_name_plural = 'TelegramSessions'

    def __str__(self):
        return '{} {}'.format(self.student.chat_id, self.tutor.chat_id)
