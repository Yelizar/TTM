from django import template
from website.access.models import CustomUser

register = template.Library()


@register.simple_tag
def get_users_online(pk, role):
    """
     If role of user is a 'Tutor' return None
     It should be changed if Tutor has the rights to find student
    """
    if role == 'Student':
        users_online = CustomUser.objects.filter(is_online=True, tutorstatus__is_active=True)
        return users_online.exclude(id=pk, role=role)
    return None
