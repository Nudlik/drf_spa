from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, status
from rest_framework.permissions import IsAdminUser, AllowAny
from rest_framework.response import Response
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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        data = serializer.data.copy()
        data.pop('password')
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)


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
