"""Модуль с представлениями приложения api."""

from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from reviews.models import Category, Genre, Review, Title

from api.serializers import (
    CategorySerializer, GenreSerializer, ReviewSerializer, TitleSerializer,
    CommentSerializer
)
from users.permissions import IsAdminOrReadOnly, IsAuthorOrModerator
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from api.filters import TitleFilter
from users.mixins import GetPermissions
from rest_framework import permissions

class GenreViewSet(viewsets.ModelViewSet):
    """Представление жанра."""

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)
    lookup_field = 'slug'

    # def perform_create(self, serializer):
    #     """Записывает в БД жанр."""
    #     serializer.save()

    def get_permissions(self):
        return (
            super().get_permissions()
            if self.action not in {'list', 'retrieve'}
            else (permissions.AllowAny(),)
        )


class CategoryViewSet(viewsets.ModelViewSet):
    """Представление категории."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)

    # def perform_create(self, serializer):
    #     """Записывает в БД категорию."""
    #     serializer.save()

    def get_permissions(self):
        return (
            super().get_permissions()
            if self.action not in {'list', 'retrieve'}
            else (permissions.AllowAny(),)
        )


class TitleViewSet(viewsets.ModelViewSet):
    """Представление произведения."""

    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, IsAdminOrReadOnly)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_permissions(self):
        return (
            super().get_permissions()
            if self.action not in {'list', 'retrieve'}
            else (permissions.AllowAny(),)
        )

    # def perform_create(self, serializer):
    #     """Записывает в БД произведение."""
    #     serializer.save()


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление отзыва."""

    serializer_class = ReviewSerializer
    permission_classes = (
        IsAuthenticatedOrReadOnly, IsAdminOrReadOnly, IsAuthorOrModerator
    )

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
        return self.get_title_or_404().comments.all()

    def perform_create(self, serializer):
        """Записывает в БД отзыв и его автора."""
        serializer.save(
            author=self.request.user,
            title=self.get_title_or_404()
        )

class CommentViewSet():
    """Представление комментария."""

    serializer_class = CommentSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthorOrModerator)

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
        """Переопределяет метод для фильтрации отзывов."""
        return self.get_review_or_404().comments.all()

    def perform_create(self, serializer):
        """Записывает в БД отзыв и его автора."""
        serializer.save(
            author=self.request.user,
            title=self.get_review_or_404()
        )

