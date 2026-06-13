from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка, что юзер является модератором"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderator").exists()


class IsNotModerator(permissions.BasePermission):
    """Проверка, что юзер не является модератором"""

    def has_permission(self, request, view):
        return not request.user.groups.filter(name="moderator").exists()
