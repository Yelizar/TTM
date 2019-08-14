from django.db import models


# Create your models here.


class TelegramUser(models.Model):
    chat_id = models.CharField(max_length=64)
    name = models.CharField(max_length=128, blank=True, null=True)

    is_active = models.BooleanField(default=False)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return '{}'.format(self.name)


class TelegramTest(models.Model):
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE)
    current_question = models.IntegerField(default=1, blank=True)
    result = models.CharField(max_length=20, default='New', blank=True)
    answers = models.CharField(max_length=4196, blank=True, null=True)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'TelegramSession'
        verbose_name_plural = 'TelegramSessions'

    def __str__(self):
        return '{}'.format(self.user.name)


class Payloads(models.Model):
    name = models.CharField(max_length=64, help_text='Name of purchase')
    label = models.CharField(max_length=64, help_text='Purchase text on button')
    amount = models.IntegerField(help_text='$9.90 = 990, $49.99 = 4999')

    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)


