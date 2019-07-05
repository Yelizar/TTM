from django.db import models

# Create your models here.


class TelegramUser(models.Model):
    chat_id = models.CharField(max_length=64)
    username = models.CharField(max_length=128, blank=True, null=True)
    name = models.CharField(max_length=128, blank=True, null=True)
    chat_type = models.CharField(max_length=64, blank=True, null=True)
    role = models.CharField(max_length=64, blank=True, null=True)
    language = models.CharField(max_length=64, blank=True, null=True)
    appear = models.CharField(max_length=64, blank=True, null=True)

    is_active = models.BooleanField(default=True)

    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'Telegram User'
        verbose_name_plural = 'Telegram Users'

    def __str__(self):
        return '{}'.format(self.username)


class TelegramSession(models.Model):
    student = models.ForeignKey(TelegramUser, related_name='Student',
                                on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    tutor = models.ForeignKey(TelegramUser, related_name="Tutor",
                              on_delete=models.CASCADE, limit_choices_to={'role': 'tutor'}, blank=True, null=True)
    language = models.CharField(max_length=64, blank=True, null=True)

    student_confirm = models.BooleanField(default=False)
    tutor_confirm = models.BooleanField(default=False)
    is_going = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    rate = models.PositiveSmallIntegerField("Session Rate", help_text='Default 5 starts', default=5)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'TelegramSession'
        verbose_name_plural = 'TelegramSessions'

    def __str__(self):
        return '{}-{}'.format(self.student, self.tutor)
