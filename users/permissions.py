from rest_framework import permissions


class EmailOwner(permissions.BasePermission):
    """ Разрешение, разрешающее редактировать только владельцам объекта. """

    def has_object_permission(self, request, view, obj):
        return obj.email == request.user.email
