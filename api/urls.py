from django.urls import include, path
from rest_framework import routers
from rest_framework.routers import DefaultRouter
from . import views

# router = DefaultRouter()
# router.register(r'users', views.UserList, basename='user')
# urlpatterns = router.urls


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    # path('', include(router.urls)),
    path('user/', views.UserList.as_view()),
    path('user/<int:pk>/', views.UserDetail.as_view()),
]