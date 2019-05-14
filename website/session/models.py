from django.db import models
from django.conf import settings


class Languages(models.Model):
    language = models.CharField('Language', max_length=32)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Language'
        verbose_name_plural = 'Languages'

    def __str__(self):
        return '{}'.format(self.language)


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

    def __str__(self):
        return '{}'.format(self.user)

    def add_coins(self, quantity):
        self.coins += quantity
        self.save()

    def remove_coins(self, quantity):
        self.coins -= quantity
        self.save()


class CommunicationMethods(models.Model):
    method = models.CharField('Method', max_length=32)

    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Communication method'
        verbose_name_plural = 'Communication methods'

    def __str__(self):
        return '{}'.format(self.method)


class Session(models.Model):
    student = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='Student',
                                   on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    tutor = models.OneToOneField(settings.AUTH_USER_MODEL, related_name="Tutor",
                                 on_delete=models.CASCADE, limit_choices_to={'role': 'Tutor'})
    session_coin = models.PositiveSmallIntegerField('Coin', help_text="Blocked coin", default=0)
    communication_method = models.OneToOneField(CommunicationMethods, on_delete=models.CASCADE)

    student_confirm = models.BooleanField(default=False)
    tutor_confirm = models.BooleanField(default=False)
    is_going = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'

    def __str__(self):
        return '{}-{}'.format(self.student, self.tutor)






