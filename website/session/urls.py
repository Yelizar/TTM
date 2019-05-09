from django.urls import path

from . import views

app_name = 'session'

urlpatterns = [

    path('<int:pk>', views.ProfileDetailView.as_view(), name='profile'),
    path('search/', views.search_view, name='search')

]