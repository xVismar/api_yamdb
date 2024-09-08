from rest_framework import permissions


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorOrModeratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            True if request.method in permissions.SAFE_METHODS
            else request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            True if request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            else request.user.is_authenticated and request.user.is_admin
            or request.user.is_moderator
        )


class ReadOnlyOrAdmin(AdminOnly):

    def has_permission(self, request, view):
        return (
            True if request.method in permissions.SAFE_METHODS
            else super().has_permission(request, view)
        )
