from django.urls import path

from . import views

app_name = 'session'

urlpatterns = [

    path('profile/<int:pk>', views.ProfileDetailsView.as_view(), name='profile'),
    path('profile/<int:pk>/<int:student>', views.ProfileDetailsView.as_view(), name='profile_action'),
    path('session/', views.SessionView.as_view(), name='session'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('connect/<int:pk>', views.connect_view, name='connect'),
    path('session-completion/<session_id>', views.SessionCompletion.as_view(), name='session-completion')
]
