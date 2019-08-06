from django.urls import path, include

from . import views

app_name = 'access'

urlpatterns = [

    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('registration-part-1/', views.RegistrationView.as_view(), name='registration'),
    path('registration-part-2/', views.RegistrationPart2View.as_view(), name='registration2'),
    path('', include('social_django.urls', namespace='social')),
    path('logout/', views.logout_view, name='logout'),
    path('application/', views.Application.as_view(), name='application')
]