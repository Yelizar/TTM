import datetime
import os

from django.contrib.auth.models import AbstractUser
from django.core.cache import cache
from django.db import models

from tplatform.models import TelegramUser
from ttm import settings
from .managers import CustomUserManager


class CustomUser(AbstractUser):
    is_online = models.BooleanField(default=False)

    objects = CustomUserManager()

    def last_seen(self):
        return cache.get('seen_%s' % self.username)

    def online(self):
        last_seen = self.last_seen()
        if last_seen:
            now = datetime.datetime.now()
            if now < last_seen + datetime.timedelta(seconds=settings.USER_ONLINE_TIMEOUT):
                self.online_status(online=True)
                return True
        self.online_status(online=False)
        return False

    def online_status(self, online=False):
        self.is_online = True if online else False
        self.save()


def tutor_directory_path(instance, filename):
    return 'website/tutors/id-{0}/cv/{1}'.format(instance.id, filename)


class Account(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True)
    telegram_user = models.OneToOneField(TelegramUser, on_delete=models.CASCADE, null=True)
    native_language = models.CharField(max_length=64, blank=True, null=True)
    learning_language = models.CharField(max_length=64, blank=True, null=True)
    appear = models.CharField(max_length=64, blank=True, null=True)
    notice = models.BooleanField(default=False)
    phone = models.CharField(max_length=17, blank=True, null=True)
    dob = models.DateField('Date of birthday', auto_now=False, auto_now_add=False, blank=True, null=True)
    cv = models.FileField(upload_to=tutor_directory_path, blank=True, null=True)

    is_status = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'Account\'s details'
        verbose_name_plural = 'Accounts details'

    def __str__(self):
        if self.user:
            return '{}'.format(self.user)
        else:
            return '{}'.format(self.telegram_user)


    def cv_name(self):
        return os.path.basename(self.cv.name)
