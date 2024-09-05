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


class CategoryViewSet(viewsets.ModelViewSet):
    """Представление категории."""

    serializer_class = CategorySerializer
    queryset = Category.objects.all()
    permission_classes = (per.IsAdminOrReadOnly,)

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
    permission_classes = (per.IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitleFilter

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        reviews = title.reviews.all()
        comments = [review.comments.all() for review in reviews]
        return comments

    # def get_permissions(self):
    #     return (
    #         super().get_permissions()
    #         if self.action not in {'list', 'retrieve'}
    #         else (permissions.AllowAny(),)
    #     )


# class ReviewViewSet(viewsets.ModelViewSet):
#     """Представление отзыва."""

#     queryset = Review.objects.all()
#     serializer_class = ReviewSerializer
#     permission_classes = (IsAuthorOrModerator,)

#     def get_permissions(self):
#         return (
#             super().get_permissions()
#             if self.action not in {'list', 'retrieve'}
#             else (permissions.AllowAny(),)
#         )

#     def get_queryset(self):
#         """Переопределяет метод для фильтрации отзывов."""
#         title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
#         return title.reviews.all()

#     def perform_create(self, serializer):
#         """Записывает в БД отзыв и его автора."""
#         title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
#         if Review.objects.filter(title=title, author=self.request.user).exists():
#             raise ValidationError('You have already reviewed this title.')
#         serializer.save(author=self.request.user, title=title)

#     def update(self, request, *args, **kwargs):
#         """Отключает метод PUT."""
#         raise MethodNotAllowed('PUT')

#     def partial_update(self, request, *args, **kwargs):
#         """Обрабатывает PATCH запросы."""
#         review = self.get_object()
#         if request.user != review.author and not request.user.is_staff:
#             raise PermissionDenied('You do not have permission to edit this review.')
#         return super().partial_update(request, *args, **kwargs)

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