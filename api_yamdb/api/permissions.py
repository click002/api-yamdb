from rest_framework import permissions


class IsAuthorOrModeratorOrAdmin(permissions.BasePermission):
    """
    Разрешение: только автор, модератор или администратор.
    """

class IsAdmin(permissions.BasePermission):
    """Доступ только для администраторов."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Администратор может всё, остальные только читать.
    Используется для управления пользователями.
    """

    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_authenticated and (
                request.user.role == 'admin' or request.user.is_superuser
            )

        if view.action == 'retrieve':
            username = view.kwargs.get('username')
            return request.user.is_authenticated and (
                request.user.username == username or
                request.user.role == 'admin' or
                request.user.is_superuser
            )

        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated

        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj == request.user or
            request.user.role == 'admin' or
            request.user.is_superuser
        )


class IsAuthorOrAdmin(permissions.BasePermission):
    """
    Доступ для автора или администратора.
    Используется для /users/me/ - пользователь может редактировать только себя.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if obj.author == request.user:
            return True

        return (request.user.role == 'moderator'
                or request.user.role == 'admin'
                or request.user.is_staff)
        return (
            obj == request.user or
            request.user.role == 'admin' or
            request.user.is_superuser
        )


class AllowAnyForSignup(permissions.BasePermission):
    """
    Специальный пермишен для регистрации - доступно всем.
    """

    def has_permission(self, request, view):
        return True
