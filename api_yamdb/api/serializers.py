from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Category, Genre, Review, Title, Comment
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from rest_framework import serializers
from rest_framework.exceptions import NotFound
from django.utils import timezone


User = get_user_model()


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра."""

    class Meta:
        """Класс с метаданными модели жанра."""

        model = Genre
        exclude = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        """Класс с метаданными модели категории."""

        model = Category
        exclude = ('id',)


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор произведений под безопасные запросы."""

    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        """Класс с метаданными модели произведения."""

        model = Title
        fields = ('id', 'name', 'year', 'description',
                  'genre', 'category', 'rating')
        read_only_fields = ('id', 'name', 'year', 'description')


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

    class Meta:
        """Класс с метаданными модели произведения."""

        model = Title
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')

    def validate_year(self, data):
        """Валидация года."""
        if data not in range(timezone.now().year + 1):
            raise serializers.ValidationError(
                'Указание не наступившего года запрещено!'
            )
        return data


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва."""

    MAX_SCORE = 10

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        """Класс с метаданными модели отзыва."""

        model = Review
        fields = ('id', 'title', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('pub_date', 'title', 'id')

    def validate(self, attrs):
        """Проверка на уникальность отзыва для пользователя и произведения."""
        request = self.context.get('request')
        if request.method == 'POST' and request:
            title_id = self.context['view'].kwargs['title_id']
            if Review.objects.filter(
                author=request.user, title_id=title_id
            ).exists():
                raise serializers.ValidationError(
                    'Вы уже оставляли отзыв на это произведение.'
                )
        if attrs['score'] not in range(self.MAX_SCORE + 1):
            raise serializers.ValidationError(
                'Ошибка! Некорректное значение оценки.'
            )
        return attrs


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        """Класс с метаданными модели комментария."""

        model = Comment
        exclude = ('review',)


class UserBaseSerializer(serializers.ModelSerializer):
    pass
    # def validate(self, attrs):
    #     if 'username' in attrs:
    #         validate_username(attrs)
    #     return attrs


class ObtainJWTSerializer(serializers.Serializer):
    """Сериалайзер для получения токена пользователем."""

    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate(self, data):
        username = data.get('username')
        confirmation_code = data.get('confirmation_code')
        if not username or not confirmation_code:
            raise serializers.ValidationError(
                "Заполните все обязательные поля."
            )
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound("Пользователь не найден.")

        confirmation_code_check = default_token_generator.check_token(
            user, token=confirmation_code
        )
        if not confirmation_code_check:
            raise serializers.ValidationError("Нет кода прав доступа.")
        data['user'] = user
        return data


class UserMeSerializer(UserBaseSerializer):

    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'role',
            'bio',
            'first_name',
            'last_name',
        )
    read_only_fields = ('role',)

    def update(self, instance, validated_data):
        validated_data.pop('role', None)
        return super().update(instance, validated_data)


class UserSerializer(UserBaseSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'role',
            'first_name',
            'last_name',
            'bio',
        )
        extra_kwargs = {
            'role': {'required': False},
            'username': {'required': True},
            'email': {'required': True},
        }


class UserSignUpSerializer(UserBaseSerializer):

    class Meta:
        model = User
        fields = ('email', 'username',)
