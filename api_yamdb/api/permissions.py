from urllib import request
from rest_framework import permissions


class AdminOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_admin


class IsAuthorOrModeratorOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return (
            True if request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            else request.user.is_authenticated and request.user.is_admin
            or request.user.is_moderator
        )


def has_object_permission(self, request, view, obj):
    if request.method in permissions.SAFE_METHODS:
        return True
    if request.user.is_authenticated:
        if request.user.is_admin or request.user.is_moderator:
            return True
        if obj.author == request.user:
            return True
    return False


class ReadOnlyOrAdmin(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.is_admin
