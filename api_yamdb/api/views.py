"""Модуль с представлениями приложения api."""

from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from reviews.models import Category, Genre, Review, Title, Comment
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.exceptions import MethodNotAllowed
from api.serializers import (
    CategorySerializer, GenreSerializer, ReviewSerializer, TitleSerializer,
    CommentSerializer
)
import users.permissions as per

from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import TitleFilter
from rest_framework import permissions
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.exceptions import ValidationError
from django.db.models import Avg


class GenreViewSet(viewsets.ModelViewSet):
    """Представление жанра."""

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
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


class TitleViewSet(viewsets.ModelViewSet):
    """Представление произведения."""

    serializer_class = TitleSerializer
    queryset = Title.objects.annotate(rating=Avg('reviews__score'))
    permission_classes = (per.IsAdminOrReadOnly,)

    def get_permissions(self):
        return (
            super().get_permissions()
            if self.action not in {'list', 'retrieve'}
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
            instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)


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
            title=self.get_title_or_404()
        )

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class CommentViewSet(viewsets.ModelViewSet):
    """Представление комментария."""

    serializer_class = CommentSerializer
    permission_classes = (per.IsAuthorOrModeratorOrReadOnly,)

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
        return self.get_review_or_404().comments.all()  # This is correct

    def perform_create(self, serializer):
        """Записывает в БД комментарий и его автора."""
        serializer.save(
            author=self.request.user,
            review=self.get_review_or_404()  # Changed from title to review
        )

    def list(self, request, title_id=None, review_id=None):
        comments = Comment.objects.filter(review_id=review_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)
