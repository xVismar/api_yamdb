"""Модуль с моделями приложения reviews."""

from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from datetime import datetime
from django.forms import ValidationError

User = get_user_model()
score_rating_range_validators = (
    MinValueValidator(0),
    MaxValueValidator(10)
)


def validate_year(value):
    """Год выпуска не может быть больше текущего."""
    if value > datetime.now().year:
        raise ValidationError(
            ('Год выпуска не может быть больше текущего'),
            params={'value': value}
        )


class BaseModel(models.Model):
    name = models.CharField(max_length=256, verbose_name='Название')
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='Идентификатор',
        help_text='Идентификатор страницы для URL; разрешены символы латиницы,'
                  ' цифры, дефис и подчёркивание.'
    )

    def __str__(self):
        return self.name


class BaseReviewComment(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст отзыва или комментария.'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время создания',
        help_text='Дата и время создания отзыва или комментария.'
    )


class Genre(BaseModel):
    """Модель жанра."""

    class Meta:
        """Класс с метаданными модели жанра."""

        ordering = ('slug',)
        verbose_name = 'жанр'
        verbose_name_plural = 'Жанры'


class Category(BaseModel):
    """Модель категории."""

    class Meta:
        """Класс с метаданными модели категории."""

        ordering = ('slug',)
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'


class Title(models.Model):
    """Модель произведения."""

    name = models.CharField(
        max_length=150,
        verbose_name='Название произведения'
    )
    year = models.PositiveSmallIntegerField(
        validators=[validate_year],
        verbose_name='Год выхода произведения'
    )
    description = models.TextField(
        blank=True,
        null=True,
        verbose_name='Описание произведения'
    )
    genre = models.ManyToManyField(Genre, verbose_name='Жанры произведения')
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория произведения'
    )

    class Meta:
        """Класс с метаданными модели произведения."""

        ordering = ('name',)
        default_related_name = 'titles'
        verbose_name = 'произведение'
        verbose_name_plural = 'Произведения'


class Review(BaseReviewComment):
    """Модель отзыва."""

    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Произведение'
    )
    score = models.PositiveSmallIntegerField(
        validators=score_rating_range_validators
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Автор отзыва или комментария.'
    )

    class Meta:
        """Класс с метаданными модели отзыва."""

        ordering = ('-pub_date',)
        default_related_name = 'reviews'
        constraints = (
            models.UniqueConstraint(
                fields=('title', 'author'),
                name='unique_title_author'
            ),
        )
        verbose_name = 'отзыв'
        verbose_name_plural = 'Отзывы'


class Comment(BaseReviewComment):
    """Модель комментария."""

    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        help_text='Автор отзыва или комментария.'
    )

    class Meta:
        """Класс с метаданными модели комментария."""

        default_related_name = 'comments'
        verbose_name = 'комментарий'
        verbose_name_plural = 'Комментарии'
