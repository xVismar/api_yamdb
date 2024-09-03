"""Модуль с сериализаторами приложения api."""

from rest_framework import serializers

from reviews.models import Category, Genre, Review, Title


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра."""

    class Meta:
        """Класс с метаданными модели жанра."""

        fields = '__all__'
        model = Genre


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        """Класс с метаданными модели категории."""

        fields = '__all__'
        model = Category


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведения."""

    class Meta:
        """Класс с метаданными модели произведения."""

        fields = '__all__'
        model = Title


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва."""

    ...

    class Meta:
        """Класс с метаданными модели отзыва."""

        fields = '__all__'
        model = Review
