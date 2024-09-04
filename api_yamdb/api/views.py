"""Модуль с представлениями приложения api."""

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from reviews.models import Category, Genre, Review, Title

from .serializers import (CategorySerializer, GenreSerializer,
                          ReviewSerializer, TitleSerializer)


class GenreViewSet(viewsets.ModelViewSet):
    """Представление жанра."""

    serializer_class = GenreSerializer
    queryset = Genre.objects.all()

    def perform_create(self, serializer):
        """Записывает в БД жанр."""
        pass


class CategoryViewSet(viewsets.ModelViewSet):
    """Представление категории."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()

    def perform_create(self, serializer):
        """Записывает в БД категорию."""
        pass


class TitleViewSet(viewsets.ModelViewSet):
    """Представление произведения."""

    serializer_class = TitleSerializer
    queryset = Title.objects.all()

    def perform_create(self, serializer):
        """Записывает в БД произведение."""
        pass


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление отзыва."""

    serializer_class = ReviewSerializer

    def get_title_or_404(self):
        """Отдаёт определенное произведение или ошибку 404."""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Переопределяет метод для фильтрации отзывов."""
        pass

    def perform_create(self, serializer):
        """Записывает в БД отзыв и его автора."""
        pass
