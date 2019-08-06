from django.urls import path

from . import views

app_name = 'session'

urlpatterns = [

    path('profile/<int:pk>', views.ProfileDetailsView.as_view(), name='profile'),
    path('initialization/<session_name>/', views.SessionInitialization.as_view(), name='initialization'),
    path('session-completion/<session_id>', views.SessionCompletion.as_view(), name='session-completion')
]