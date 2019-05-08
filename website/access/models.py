from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    ROLE = (('Student', 'Student'),
            ('Tutor', 'Tutor'))
    role = models.CharField(max_length=8, choices=ROLE, help_text='Role can\'t be changed after', null=True, blank=True)



