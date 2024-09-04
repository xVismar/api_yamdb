"""Модуль с представлениями приложения api."""

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from reviews.models import Category, Genre, Review, Title

from .serializers import (CategorySerializer, GenreSerializer,
                          ReviewSerializer, TitleSerializer, CommentSerializer)
from users.permissions import IsAuthor, IsModerator, IsAdminOrReadOnly


class GenreViewSet(viewsets.ModelViewSet):
    """Представление жанра."""

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()
    permission_classes = (IsAdminOrReadOnly,)

    def perform_create(self, serializer):
        """Записывает в БД жанр."""
        serializer.save()


class CategoryViewSet(viewsets.ModelViewSet):
    """Представление категории."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (IsAdminOrReadOnly,)

    def perform_create(self, serializer):
        """Записывает в БД категорию."""
        serializer.save()


class TitleViewSet(viewsets.ModelViewSet):
    """Представление произведения."""

    serializer_class = TitleSerializer
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)

    def perform_create(self, serializer):
        """Записывает в БД произведение."""
        serializer.save()


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление отзыва."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAdminOrReadOnly, IsAuthor, IsModerator)

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
    permission_classes = (IsAdminOrReadOnly, IsAuthor, IsModerator)

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
