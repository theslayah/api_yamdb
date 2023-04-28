from rest_framework import serializers
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сеарилизатор для Usera."""

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового пользователя."""

    class Meta:
        model = User
        fields = ('username', 'email',)

    def validate_username(self, data):
        if data['username'] == 'me':
            raise serializers.ValidationError(
                "Использовать имя 'me' в качестве username запрещено."
            )
        return data


class TokenSeializer(serializers.ModelSerializer):
    """Сериализатор для JWT-токена."""
    username = serializers.CharField()
    confiramtion_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_code',)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализует данные запросов
    эндпоинтов r'categories'.
    """

    class Meta:
        model = Category
        exclude = ('id',)
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    """Сериализует данные запросов
    эндпоинтов r'genres'.
    """

    class Meta:
        model = Genre
        exclude = ('id',)
        lookup_field = 'slug'


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализует данные запросов
    эндпоинтов r'titles', если
    self.action in ("retrieve", "list").
    """
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug', queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'


class ReadOnlyTitleSerializer(serializers.ModelSerializer):
    """Сериализует данные запросов
    эндпоинтов r'titles', если
    self.action not in ("retrieve", "list").
    """
    rating = serializers.IntegerField(read_only=True)
    genre = GenreSerializer(many=True)
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'rating', 'genre', 'category'
        )


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализует данные запросов
    эндпоинтов r'reviews'.
    """
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Review
        exclude = ('title',)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализует данные запросов
    эндпоинтов r'comments'.
    """
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username'
    )

    class Meta:
        model = Comment
        exclude = ('review',)
