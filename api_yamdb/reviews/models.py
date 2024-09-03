"""Модуль с моделями приложения reviews."""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()

score_rating_range_validators = (
    MinValueValidator(0),
    MaxValueValidator(10)
)


class Genre(models.Model):
    """Модель жанра."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        """Класс с метаданными модели жанра."""

        ordering = ('slug',)


class Category(models.Model):
    """Модель категории."""

    name = models.CharField(max_length=256)
    slug = models.SlugField(max_length=50, unique=True)

    class Meta:
        """Класс с метаданными модели категории."""

        ordering = ('slug',)


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(max_length=256)
    year = models.PositiveSmallIntegerField()
    description = models.TextField()
    genre = models.ManyToManyField(
        Genre, related_name='titles'
    )
    category = models.ManyToManyField(
        Category, related_name='titles'
    )
    rating = models.PositiveSmallIntegerField(
        default=None, validators=score_rating_range_validators
    )

    class Meta:
        """Класс с метаданными модели произведения."""

        ordering = ('name', 'year')


class Review(models.Model):
    """Модель отзыва."""

    title = models.ForeignKey(
        Title, on_delete=models.CASCADE, related_name='reviews'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.PositiveSmallIntegerField(
        validators=score_rating_range_validators
    )
    pub_date = models.DateTimeField(auto_now_add=True)
