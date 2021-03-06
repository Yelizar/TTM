from django.db import models
from website.access.models import Account
from .managers import SessionCoinsManager, SessionManager


class SessionCoins(models.Model):
    """
    This model will be completely reworked when fee payment is implemented.
    """
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
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

    student_confirm = models.NullBooleanField()
    tutor_confirm = models.NullBooleanField()
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


class Notifications(models.Model):
    sender = models.ForeignKey(Account, related_name='Sender',
                               on_delete=models.CASCADE)
    recipient = models.ForeignKey(Account, related_name="Recipient",
                                  on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    message = models.CharField(max_length=1024, blank=True, null=True)
    is_read = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)

    def mark_as_read(self):
        if self.is_read is False:
            self.is_read = True
            self.save()


class Payments(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    currency = models.CharField(max_length=4)
    payload = models.CharField(max_length=64, help_text='Name of purchase')
    provider = models.TextField(help_text='Provider payment charger id')
    total = models.FloatField(help_text='Total price')

    created = models.DateTimeField(auto_now=False, auto_now_add=True)
