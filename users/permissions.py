from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    message = "Проверка, что юзер является модератором"

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderator").exists()
