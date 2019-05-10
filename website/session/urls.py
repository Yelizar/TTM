from django.urls import path

from . import views

app_name = 'session'

urlpatterns = [

    path('profile/<int:pk>', views.ProfileDetailView.as_view(), name='profile'),
    path('profile/update-tutor-details/<int:pk>', views.TutorDetailsUpdateView.as_view(), name='update-tutor-details'),
    path('search/', views.search_view, name='search'),


]