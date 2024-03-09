from django.contrib.auth import get_user_model
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser, AllowAny

from users.permissions import EmailOwner
from users.serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
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
