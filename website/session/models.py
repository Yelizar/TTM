from django.db import models
from django.conf import settings
from website.access.models import Account
from .managers import ChannelRoomManager, ChannelNamesManager, SessionCoinsManager, SessionManager
from django.urls import reverse


class SessionCoins(models.Model):
    """
    This model will be completely reworked when fee payment is implemented.
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    coins = models.PositiveSmallIntegerField('Coins', help_text="1 coin = 1 session", default=0)

    is_active = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'Session coin'
        verbose_name_plural = 'Session coins'

    objects = SessionCoinsManager()

    def __str__(self):
        return '{}'.format(self.user)


class Session(models.Model):
    student = models.ForeignKey(Account, related_name='Student',
                                on_delete=models.CASCADE,)
    tutor = models.ForeignKey(Account, related_name="Tutor",
                              on_delete=models.CASCADE, blank=True, null=True)
    language = models.CharField(max_length=64, blank=True, null=True)

    student_confirm = models.BooleanField(default=False)
    tutor_confirm = models.BooleanField(default=False)
    is_going = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rate = models.PositiveSmallIntegerField("Session Rate", help_text='Default 5 starts', default=5)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    objects = SessionManager()

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'

    def __str__(self):
        return '{}'.format(self.student)



