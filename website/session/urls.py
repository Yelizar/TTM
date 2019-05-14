from django.urls import path

from . import views

app_name = 'session'

urlpatterns = [

    path('profile/<int:pk>', views.ProfileDetailsView.as_view(), name='profile'),
    path('profile/update-details/<int:pk>', views.TutorDetailsUpdateView.as_view(), name='update-details'),
    path('search/', views.search_view, name='search'),


]