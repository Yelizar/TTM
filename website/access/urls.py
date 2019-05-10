from django.urls import path, include

from . import views

app_name = 'access'

urlpatterns = [

    # temporary "redirect" to home page
    path('', views.HomeView.as_view(), name='home'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('registration-part-1/', views.RegistrationView.as_view(), name='registration'),
    path('registration-part-2/', views.RegistrationPart2View.as_view(), name='registration2'),
    path('registration-part-3/', views.RegistrationPart3View.as_view(), name='registration3'),
    path('', include('social_django.urls', namespace='social')),
    path('logout/', views.logout_view, name='logout')
]