from django import template
from website.session.utils import get_logged_users
register = template.Library()


@register.simple_tag
def get_users_online(id, role):
    """
     If role of user is a 'Tutor' return None
     It should be changed if Tutor has the rights to find student
    """
    if role == 'Student':
        users_online = get_logged_users()
        return users_online.exclude(id=id, role=role)
    return None
