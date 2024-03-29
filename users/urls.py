from django.urls import path, include
from rest_framework import routers

from users import apps
from users.views import UserViewSet, CustomTokenObtainPairView, CustomTokenRefreshView

app_name = apps.UsersConfig.name

router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='users')

urlpatterns = [
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', CustomTokenRefreshView.as_view(), name='token_refresh'),

    path('', include(router.urls)),
]
