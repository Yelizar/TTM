from django.urls import path

from . import views

app_name = 'website'

urlpatterns = [

    path('registration/', views.Registration.as_view(), name='registration'),
]