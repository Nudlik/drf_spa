from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from users.permissions import EmailOwner
from users.serializers import UserSerializer
from users.yasg import user_docs, token_docs_pair, token_docs_refresh


class UserViewSet(viewsets.ModelViewSet):
    __doc__ = user_docs

    serializer_class = UserSerializer
    queryset = get_user_model().objects.all()
    perms_methods = {
        'create': [AllowAny],
        'update': [EmailOwner | IsAdminUser],
        'partial_update': [EmailOwner | IsAdminUser],
        'destroy': [EmailOwner | IsAdminUser],
    }

    def get_permissions(self):
        self.permission_classes = self.perms_methods.get(self.action, self.permission_classes)
        return [permission() for permission in self.permission_classes]


class CustomTokenObtainPairView(TokenObtainPairView):
    __doc__ = token_docs_pair

    @swagger_auto_schema(operation_summary='Получение пользовательского токена.')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    __doc__ = token_docs_refresh

    @swagger_auto_schema(operation_summary='Обновление пользовательского токена.')
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
