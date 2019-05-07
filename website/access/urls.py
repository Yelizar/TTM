from django.urls import path, include

from . import views

app_name = 'access'

urlpatterns = [

    path('registration/', views.Registration.as_view(), name='registration'),
    path('', include('social_django.urls', namespace='social')),
    path('logout/', views.logout_view, name='logout')
]