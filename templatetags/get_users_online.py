from django import template
from website.session.utils import get_active_tutors
register = template.Library()


@register.simple_tag
def get_users_online(pk, role):
    """
     If role of user is a 'Tutor' return None
     It should be changed if Tutor has the rights to find student
    """
    if role == 'Student':
        users_online = get_active_tutors()
        return users_online.exclude(id=pk, role=role)
    return None
