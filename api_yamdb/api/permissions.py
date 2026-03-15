from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Доступ только для администраторов."""

    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Администратор может всё, остальные только читать.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and (
            request.user.role == 'admin' or request.user.is_superuser
        )


class IsAdminOrModeratorOrReadOnly(permissions.BasePermission):
    """
    Модератор и администратор могут редактировать и удалять.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj.author == request.user
            or request.user.role == 'moderator'
            or request.user.role == 'admin'
            or request.user.is_superuser
        )


class IsAuthorOrAdmin(permissions.BasePermission):
    """
    Доступ для автора или администратора.
    """

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            obj == request.user
            or request.user.role == 'admin'
            or request.user.is_superuser
        )


class IsAdminUserOrReadOnlyForList(permissions.BasePermission):
    """
    Для списка пользователей - только админ, для остального - аутентификация.
    """

    def has_permission(self, request, view):
        if view.action == 'list':
            return request.user.is_authenticated and (
                request.user.role == 'admin' or request.user.is_superuser
            )
        if view.action == 'retrieve':
            username = view.kwargs.get('username')
            return request.user.is_authenticated and (
                request.user.username == username
                or request.user.role == 'admin'
                or request.user.is_superuser
            )
        return request.user.is_authenticated


class AllowAnyForSignup(permissions.BasePermission):
    """
    Специальный пермишен для регистрации - доступно всем.
    """

    def has_permission(self, request, view):
        return True
