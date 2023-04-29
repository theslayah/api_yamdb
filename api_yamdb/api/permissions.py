from rest_framework import permissions


class IsAdminOnly(permissions.BasePermission):
    """Разрешение для админа."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin)


class IsAdminOrReadOnly(permissions.BasePermission):
    """Разрешение для админа или только просмотр для остальных."""
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return (
            request.user.is_admin
            if request.user.is_authenticated else False
        )


class IsAuthorAdminModeratorPermission(permissions.BasePermission):
    """Разрешение для автора, админа или модератора."""
    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_moderator
            or request.user.is_admin
        )
