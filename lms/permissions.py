from rest_framework.permissions import IsAuthenticated


class IsOwner(IsAuthenticated):
    """Проверка, что юзер является владельцем объекта"""

    message = "Вы не являетесь владельцем этого объекта"

    def has_object_permission(self, request, view, obj):
        if not super().has_permission(request, view):
            return False
        if not hasattr(obj, "owner"):
            return False
        return request.user == obj.owner
