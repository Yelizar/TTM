from django.db import models
from django.conf import settings
from .managers import ChannelRoomManager, ChannelNamesManager, CommunicationMethodNumberManager
from django.urls import reverse


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


class CommunicationMethodNumber(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    com_method = models.ForeignKey(CommunicationMethods, on_delete=models.CASCADE)
    number = models.CharField("Number", max_length=128)

    is_active = models.BooleanField(default=True)

    objects = CommunicationMethodNumberManager()

    class Meta:
        verbose_name = 'Communication method number'
        verbose_name_plural = 'Communication method numbers'

    def __str__(self):
        return '{}'.format(self.com_method)


class Session(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='Student',
                                on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="Tutor",
                              on_delete=models.CASCADE, limit_choices_to={'role': 'Tutor'})
    session_coin = models.PositiveSmallIntegerField('Coin', help_text="Blocked coin", default=0)
    language = models.ForeignKey(Languages, on_delete=models.CASCADE)
    communication_method = models.ForeignKey(CommunicationMethods, on_delete=models.CASCADE)

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


class ChannelRoom(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='RoomHolder',
                                on_delete=models.CASCADE, limit_choices_to={'role': 'Student'})

    tutor = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name="Visitor", limit_choices_to={'role': 'Tutor'},
                                   default=None, blank=True)

    is_active = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    objects = ChannelRoomManager()

    class Meta:
        verbose_name = 'Channel'
        verbose_name_plural = 'Channels'

    def __str__(self):
        return 'Channel-{}'.format(self.student)

    def get_absolute_url(self):
        return reverse('session:session-initialization', kwargs={'session_name': self.student})


class ChannelNames(models.Model):
    channel = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    channel_name = models.CharField('Channel Name', max_length=36)
    is_active = models.BooleanField(default=True)

    objects = ChannelNamesManager()

    class Meta:
        verbose_name = 'Channel Name'
        verbose_name_plural = 'Channels Names'

    def __str__(self):
        return '{}'.format(self.channel)



