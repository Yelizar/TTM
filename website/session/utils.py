from django.contrib.sessions.models import Session
from website.access.models import CustomUser
from django.utils import timezone


def get_active_tutors():
    """create a list with tutors, who is looking for a session"""
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    online_users_id_list = []

    for session in sessions:
        data = session.get_decoded()
        online_users_id_list.append(data.get('_auth_user_id', None))

    return CustomUser.objects.filter(id__in=online_users_id_list, tutorstatus__is_active=True)
