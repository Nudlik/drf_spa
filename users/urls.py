from django.urls import path, include
from rest_framework import routers

from users import apps
from users.views import UserViewSet

app_name = apps.UsersConfig.name

router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls))
]
