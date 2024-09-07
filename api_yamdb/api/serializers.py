from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Category, Genre, Review, Title, Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from django.conf import settings
from rest_framework import serializers
from api_yamdb.constants import (
    MAX_LENGTH_EMAIL,
    MAX_LENGTH_USERNAME,
    MAX_VALUE_SCORE,
    MIN_VALUE_SCORE,
)
from reviews.models import Category, Genre, Title, Comment, Review, User
from api.validators import ValidateUsername, validate_year


User = get_user_model()

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


class TitleSafeSerializer(serializers.ModelSerializer):
    """Сериализатор произведений под безопасные запросы."""

    genre = GenreSerializer(many=True)
    category = CategorySerializer()
    rating = serializers.IntegerField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating')
        read_only_fields = ('__all__',)


class TitleUnsafeSerializer(serializers.ModelSerializer):
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
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author', 'pub_date', 'title', 'id')

    def validate(self, attrs):
        """Проверка на уникальность отзыва для пользователя и произведения."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            if Review.objects.filter(
                author=request.user, title_id=title_id
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение.'
                )
        return attrs

    def score_validator(self, value):
        if MIN_VALUE_SCORE < value <MAX_VALUE_SCORE:
            return value
        return ValidationError(f'Оценка должна быть в пределах от {MIN_VALUE_SCORE} до {MAX_VALUE_SCORE}!')


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = SlugRelatedField(slug_field='username', read_only=True)
    # title = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


# class ObtainJWTSerializer(serializers.Serializer):
#     """Сериалайзер для получения токена пользователем."""

#     username = serializers.CharField()
#     confirmation_code = serializers.CharField()

#     def validate(self, data):
#         username = data.get('username')
#         confirmation_code = data.get('confirmation_code')
#         if not username or not confirmation_code:
#             raise serializers.ValidationError(
#                 "Заполните все обязательные поля."
#             )
#         try:
#             user = User.objects.get(username=username)
#         except User.DoesNotExist:
#             raise NotFound("Пользователь не найден.")

#         confirmation_code_check = default_token_generator.check_token(
#             user, token=confirmation_code
#         )
#         if not confirmation_code_check:
#             raise serializers.ValidationError("Нет кода прав доступа.")
#         data['user'] = user
#         return data


# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User
#         fields = (
#             'username',
#             'email',
#             'role',
#             'first_name',
#             'last_name',
#             'bio',
#         )
#         extra_kwargs = {
#             'role': {'required': False},
#             'username': {'required': True},
#             'email': {'required': True},
#         }

#     def update(self, instance, validated_data):
#         validated_data.pop('role', None)
#         return super().update(instance, validated_data)


# class UserSignUpSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = User
#         fields = ('email', 'username',)

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

   