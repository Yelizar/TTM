import datetime
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from .models import CustomUser
from django.contrib.sessions.models import Session
from website.session.models import Session as InitializedSessions

from django.shortcuts import HttpResponse, reverse, redirect
from django.utils import timezone


class ActiveUserMiddleware(MiddlewareMixin):

    def process_request(self, request):
        current_user = request.user
        if current_user.is_authenticated:
            now = datetime.datetime.now()
            cache.set('seen_%s' % (current_user.username), now,
                      settings.USER_LASTSEEN_TIMEOUT)
            # Checks for completeness of sessions
            initialized_session = InitializedSessions.objects.get_last_session(current_user=current_user)
            if initialized_session:
                if request.path != '/session-completion/{}'.format(initialized_session.id):
                    return redirect(
                        reverse('session:session-completion', kwargs={'session_id': initialized_session.id}))

        # пока нет AJAX выполняет функцию обновления Online Offline status через middleware
        # -----------------------------------------------------------------------------------
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        authorized_users_id_list = []
        online_users = CustomUser.objects.filter(is_online=True)
        for session in sessions:
            data = session.get_decoded()
            authorized_users_id_list.append(data.get('_auth_user_id', None))
        online_users = online_users.exclude(id__in=authorized_users_id_list)
        for user in online_users:
            user.online_status(online=False)
        # -----------------------------------------------------------------------------------




