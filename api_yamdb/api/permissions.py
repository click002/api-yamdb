from rest_framework import permissions


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешение: только автор, модератор или администратор.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.author == request.user:
            return True

        return (request.user.role == 'moderator'
                or request.user.role == 'admin'
                or request.user.is_staff)
