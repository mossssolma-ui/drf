from rest_framework import permissions


class IsModerator(permissions.BasePermission):
    """Проверка, что юзер является модератором"""

    def has_permission(self, request, view):
        return request.user.groups.filter(name="moderator").exists()

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)
