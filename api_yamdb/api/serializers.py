
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.relations import SlugRelatedField
from reviews.validators import ValidateUsername, validate_year
from reviews.constants import (
    MAX_LENGTH_EMAIL, MAX_LENGTH_USERNAME, MAX_VALUE_SCORE, MIN_VALUE_SCORE
)
from reviews.models import Category, Comment, Genre, Review, Title, User


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра."""

    class Meta:
        model = Genre
        exclude = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        model = Category
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор произведений под безопасные запросы."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating')
        read_only_fields = ('__all__',)


class TitleModificateSerializer(serializers.ModelSerializer):
    """Сериализатор произведений под небезопасные запросы."""

    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all(),
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )
    year = serializers.IntegerField(validators=[validate_year])

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('pub_date', 'title', 'id')

    def validate(self, attrs):
        """Проверка оценки и уникальности отзыва."""
        request = self.context.get('request')
        if (
            request and request.method == 'POST' and Review.objects.filter(
                author=request.user,
                title_id=self.context['view'].kwargs['title_id']).exists()
        ):
            raise ValidationError(
                'Вы уже оставляли отзыв на это произведение.'
            )
        score = attrs.get('score')
        return (
            attrs if score is not None
            and MIN_VALUE_SCORE <= score <= MAX_VALUE_SCORE
            else ValidationError(
                f'Оценка должна быть в пределах от {MIN_VALUE_SCORE} до '
                f'{MAX_VALUE_SCORE}!'
            )
        )


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = SlugRelatedField(slug_field='username', read_only=True)
    text = serializers.CharField(required=True)

    class Meta:
        """Класс с метаданными модели комментария."""

        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class UserSerializer(serializers.ModelSerializer, ValidateUsername):

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )


class UserProfileSerializer(UserSerializer):

    class Meta(UserSerializer.Meta):
        fields = '__all__'
        read_only_fields = ('role',)


class SignUpSerializer(serializers.Serializer, ValidateUsername):
    email = serializers.EmailField(
        max_length=MAX_LENGTH_EMAIL,
        required=True
    )
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True
    )


class ObtainJWTSerializer(serializers.Serializer, ValidateUsername):
    confirmation_code = serializers.CharField(
        max_length=settings.MAX_LENGTH_CONFIRMATION_CODE,
        required=True
    )
    username = serializers.CharField(
        max_length=MAX_LENGTH_USERNAME,
        required=True
    )
