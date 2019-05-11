from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
import os


class CustomUser(AbstractUser):
    ROLE = (('Student', 'Student'),
            ('Tutor', 'Tutor'))
    role = models.CharField(max_length=8, choices=ROLE, help_text='Role can\'t be changed after', null=True, blank=True)


def tutor_directory_path(instance, filename):
    return 'website/tutors/id-{0}_{1}/cv/{2}'.format(instance.user.id, instance.user.username, filename)


class TutorDetails(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Tutor'},
                                primary_key=True)
    phone_regex = RegexValidator(regex=r'^\+?1?\d{9,15}$',
                                 message="Phone number must be entered in the format:"
                                         " '+999999999'. Up to 15 digits allowed.")
    phone_number = models.CharField(validators=[phone_regex], max_length=17, blank=True, null=True)
    dob = models.DateField('Date of birthday', auto_now=False, auto_now_add=False, blank=True, null=True)
    short_resume = models.CharField('resume', max_length=2048, blank=True, null=True)
    cv = models.FileField(upload_to=tutor_directory_path, blank=True, null=True)

    is_active = models.BooleanField('Approved', default=False)
    created = models.DateTimeField(auto_now=False, auto_now_add=True)
    updated = models.DateTimeField(auto_now=True, auto_now_add=False)

    class Meta:
        verbose_name = 'Tutor\'s details'
        verbose_name_plural = 'Tutor\'s details'

    def __str__(self):
        return '{}'.format(self.user)

    def cv_name(self):
        return os.path.basename(self.cv.name)


class TutorStatus(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'Tutor'},
                                primary_key=True)
    is_active = models.BooleanField('Waiting Session', default=False)

    class Meta:
        verbose_name = 'Tutor\'s status'
        verbose_name_plural = 'Tutor\'s statuses'

    def __str__(self):
        return '{}'.format(self.user)


