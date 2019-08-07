from django.urls import path

from . import views

app_name = 'session'

urlpatterns = [

    path('profile/<int:pk>', views.ProfileDetailsView.as_view(), name='profile'),
    path('session/', views.SessionView.as_view(), name='session'),
    path('history/', views.HistoryView.as_view(), name='history'),
    path('session-completion/<session_id>', views.SessionCompletion.as_view(), name='session-completion')
]