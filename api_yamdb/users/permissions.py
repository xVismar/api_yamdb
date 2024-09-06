from rest_framework import permissions
from rest_framework.response import Response
from rest_framework import status, permissions

class BaseRolePermission(permissions.BasePermission):
    role_check = None

    def has_permission(self, request, view):
        return request.user.is_authenticated and self.role_check(request.user)

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and self.role_check(request.user)

class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and request.user.is_admin
        )

    def has_object_permission(self, request, view, obj):
        return (
           request.user.is_authenticated and request.user.is_admin
        )

class AdminOnlyPermission(BaseRolePermission):
    role_check = lambda self, user: user.is_admin


class IsAuthorOrModeratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if view.action in {'delete', 'patch'}:
            if obj.author == request.user:
                return True
            if request.user.is_staff or request.user.is_moderator:
                return True
            return False
        if view.action == 'create':
            return request.user.is_authenticated
        return True


from rest_framework.permissions import BasePermission

class IsAuthorOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user
