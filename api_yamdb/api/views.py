"""Модуль с представлениями приложения api."""

from urllib import request
from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from reviews.models import Category, Genre, Review, Title, Comment
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import MethodNotAllowed
from api.serializers import (
    CategorySerializer, GenreSerializer, ReviewSerializer, TitleSafeSerializer, TitleUnsafeSerializer,
    CommentSerializer
)
import users.permissions as per
from rest_framework import viewsets, pagination

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import TitleFilter
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.exceptions import ValidationError
from django.db.models import Avg
from rest_framework.pagination import PageNumberPagination
from django.db.models import Count

class GenreViewSet(viewsets.ModelViewSet):
    """Представление жанра."""

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (per.IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'
    pagination_class = pagination.PageNumberPagination 

    def get_permissions(self):
        return (
            super().get_permissions()
            if self.action not in {'list', 'retrieve'}
            else (permissions.AllowAny(),)
        )

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().retrieve(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def filter_queryset(self, queryset):
        genre_slug = self.request.query_params.get('genre')
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        return queryset

class CategoryViewSet(viewsets.ModelViewSet):
    """Представление категории."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (per.IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    def get_permissions(self):
        return (
            super().get_permissions()
            if self.action not in {'list', 'retrieve'}
            else (permissions.AllowAny(),)
        )

    def retrieve(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().retrieve(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().partial_update(request, *args, **kwargs)


# class TitleViewSet(viewsets.ModelViewSet):
#     serializer_class = TitleSerializer
#     queryset = Title.objects.all()
#     permission_classes = (per.IsAdminOrReadOnly,)

#     def get_permissions(self):
#         return (
#             super().get_permissions()
#             if self.action not in {'list', 'retrieve'}
#             else (permissions.AllowAny(),)
#         )

#     def get_object(self):
#         return get_object_or_404(Title, id=self.kwargs.get('pk'))

#     def retrieve(self, request, *args, **kwargs):
#         title = self.get_object()
#         serializer = self.get_serializer(title)
#         return Response(serializer.data)

#     def update(self, request, *args, **kwargs):
#         if not request.user.is_staff:
#             return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         return super().update(request, *args, **kwargs)

#     # def partial_update(self, request, *args, **kwargs):
#     #     if not request.user.is_staff:
#     #         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
#     #     return super().partial_update(request, *args, **kwargs)

class TitleViewSet(viewsets.ModelViewSet):
    """Представление произведения."""

    queryset = Title.objects.all()
    permission_classes = (per.IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('genre__slug',)


    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return TitleSafeSerializer
        return TitleUnsafeSerializer

    def get_permissions(self):
        return (
            super().get_permissions()
            if self.action not in ['retrieve', 'list']
            else (permissions.AllowAny(),)
        )

    def create(self, request, *args, **kwargs):
        """Создает новый объект Title и возвращает статус 201."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)
    def filter_queryset(self, queryset):
        genre_slug = self.request.query_params.get('genre')
        if genre_slug:
            queryset = queryset.filter(genre__slug=genre_slug)
        return queryset
    # def create(self, request, *args, **kwargs):
    #     # Ensure you are not trying to set read-only fields
    #     return super().create(request, *args, **kwargs)

    # def update(self, request, *args, **kwargs):
    #     # Ensure you are not trying to set read-only fields
    #     return super().update(request, *args, **kwargs)

class ReviewViewSet(viewsets.ModelViewSet):
    """Представление отзыва."""

    serializer_class = ReviewSerializer
    permission_classes = (per.IsAuthorOrModeratorOrReadOnly,)

    def get_permissions(self):
        return (
            super().get_permissions()
            if self.action not in {'list', 'retrieve'}
            else (permissions.AllowAny(),)
        )

    def get_title_or_404(self):
        """Отдаёт определенное произведение или ошибку 404."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Переопределяет метод для фильтрации отзывов."""
        return self.get_title_or_404().reviews.all()

    def perform_create(self, serializer):
        """Записывает в БД отзыв и его автора."""
        serializer.save(
            author=self.request.user,
            title=self.get_title_or_404())

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().partial_update(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentViewSet(viewsets.ModelViewSet):
    """Представление комментария."""

    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = (per.IsAuthorOrModeratorOrReadOnly,)
    http_method_names = ['get', 'post', 'patch', 'delete']

    # def get_permissions(self):
    #     if self.action in ['update', 'partial_update', 'destroy']:
    #         self.permission_classes = (per.IsAuthorOrReadOnly,)
    #     if self.action in {'list', 'retrieve'}:
    #         self.permission_classes = (permissions.AllowAny,)
    #     return super().get_permissions()

    def get_permissions(self):
        return (
            super().get_permissions()
            if self.action not in {'list', 'retrieve'}
            else (permissions.AllowAny(),)
        )

    def get_review_or_404(self):
        """Отдает определенный отзыв или ошибку 404."""
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        """Переопределяет метод для фильтрации комментариев."""
        return self.get_review_or_404().comments.all().order_by('pub_date')

    def perform_create(self, serializer):
        """Записывает в БД комментарий и его автора."""
        serializer.save(
            author=self.request.user,
            review=self.get_review_or_404()
        )

    # def list(self, request, title_id=None, review_id=None):
    #     comments = self.get_queryset()
    #     page = self.paginate_queryset(comments)
    #     if page is not None:
    #         serializer = self.get_serializer(page, many=True)
    #         return self.get_paginated_response(serializer.data)
    #     serializer = self.get_serializer(comments, many=True)
    #     return Response(serializer.data)

    # def partial_update(self, request, *args, **kwargs):
    #     if (
    #         not request.user.is_staff
    #         or not self.request.user == Comment.objects.get(
    #             id=self.kwargs['comment_id']
    #         )
    #         or not request.user.is_moderator
    #     ):
    #         return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)
    #     return super().partial_update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        comment = get_object_or_404(Comment, id=self.kwargs.get('comment_id'))
        if self.request.user != comment.author:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return self.update(request, *args, **kwargs)