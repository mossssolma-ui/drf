from rest_framework import permissions
from rest_framework.permissions import IsAuthenticated


class IsModerator(permissions.BasePermission):
    """Проверка, что юзер является модератором"""

    def has_permission(self, request, view):
        if request.user.is_anonymous:
            return False
        return request.user.groups.filter(name="moderator").exists()

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class IsPaymentOwner(IsAuthenticated):
    """Проверка, что юзер является владельцем платежа"""

    message = "Вы не являетесь владельцем этого платежа"

    def has_object_permission(self, request, view, obj):
        if not super().has_permission(request, view):
            return False
        if not hasattr(obj, "user"):
            return False
        return request.user == obj.user
