from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """Проверка, что юзер является владельцем объекта"""

    def has_object_permission(self, request, view, obj):
        if not hasattr(obj, "owner"):
            return False
        return request.user == obj.owner
