from django.contrib.sessions.models import Session
from website.access.models import CustomUser
from django.utils import timezone


def get_logged_users():
    sessions = Session.objects.filter(expire_date__gte=timezone.now())
    online_users_id_list = []

    for session in sessions:
        data = session.get_decoded()
        print(data)
        online_users_id_list.append(data.get('_auth_user_id', None))

    return CustomUser.objects.filter(id__in=online_users_id_list)
