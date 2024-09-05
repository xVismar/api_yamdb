from rest_framework import serializers
from rest_framework.relations import SlugRelatedField
from reviews.models import Category, Genre, Review, Title, Comment


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор жанра."""

    class Meta:
        """Класс с метаданными модели жанра."""

        model = Genre
        fields = ('id', 'name', 'slug')



class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор категории."""

    class Meta:
        """Класс с метаданными модели категории."""

        model = Category
        fields = ('id', 'name', 'slug')

class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор произведения."""

    genre = serializers.SlugRelatedField(
        many=True,
        slug_field='slug',
        queryset=Genre.objects.all()
    )
    category = CategorySerializer()


    class Meta:
        """Класс с метаданными модели произведения."""

        model = Title
        fields = ('id', 'name', 'year', 'genre', 'category', 'description' )
        read_only_fields = ('rating',)



# class TitleSerializer(serializers.ModelSerializer):
#     """Сериализатор произведения."""

#     genre = GenreSerializer(many=True, read_only=True)
#     category = CategorySerializer(read_only=True)
#     rating = serializers.IntegerField(read_only=True)

#     class Meta:
#         """Класс с метаданными модели произведения."""

#         model = Title
#         fields = ('id', 'name', 'year', 'description', 'genre', 'category', 'rating')
#         read_only_fields = ('rating',)


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор отзыва."""

    author = serializers.SlugRelatedField(slug_field='username', read_only=True)
    title = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        """Класс с метаданными модели отзыва."""

        model = Review
        fields = ('title', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('author', 'pub_date')

    def validate(self, data):
        """Проверка на уникальность отзыва для пользователя и произведения."""
        request = self.context.get('request')
        if request and request.method == 'POST':
            title_id = self.context['view'].kwargs.get('title_id')
            if Review.objects.filter(author=request.user, title_id=title_id).exists():
                raise serializers.ValidationError('Вы уже оставляли отзыв на это произведение.')
        return data


# class ReviewSerializer(serializers.ModelSerializer):
#     """Сериализатор модели Review."""

#     author = serializers.SlugRelatedField(
#         read_only=True,
#         slug_field='username',
#     )

#     class Meta:
#         model = Review
#         fields = ('id', 'text', 'author', 'score', 'pub_date')
#         read_only_fields = ('author', 'pub_date')

#     def validate(self, data):
#         if self.context['request'].method != 'POST':
#             return data
#         if Review.objects.filter(
#             title=self.context['view'].kwargs['title_id'],
#             author=self.context['request'].user,
#         ).exists():
#             raise serializers.ValidationError('Вы уже оставили отзыв.')
#         return data


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор комментария."""

    author = SlugRelatedField(slug_field='username', read_only=True)
    title = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        """Класс с метаданными модели комментария."""

        model = Comment
        fields = '__all__'
        read_only_fields = ('review',)



# class ReviewSerializer(serializers.ModelSerializer):
#     """Сериализатор отзыва."""

#     author = SlugRelatedField(slug_field='username', read_only=True)

#     class Meta:
#         """Класс с метаданными модели отзыва."""

#         model = Review
#         fields = '__all__'



# class CommentSerializer(serializers.ModelSerializer):
#     """Сериализатор комментария."""

#     author = SlugRelatedField(slug_field='username', read_only=True)

#     class Meta:
#         """Класс с метаданными модели комментария."""

#         model = Comment
#         fields = '__all__'
#         read_only_fields = ('review',)