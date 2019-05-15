from django.urls import path

from . import views

app_name = 'session'

urlpatterns = [

    path('profile/<int:pk>', views.ProfileDetailsView.as_view(), name='profile'),
    path('profile/update-t-details/<int:pk>', views.TutorDetailsUpdateView.as_view(), name='update-tutor-details'),
    path('profile/update-s-details/<int:pk>', views.StudentDetailsUpdateView.as_view(), name='update-student-details'),
    path('search/', views.search_view, name='search'),


]