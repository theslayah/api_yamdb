from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сеарилизатор для Usera."""
    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z',
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    email = serializers.EmailField(max_length=254,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class CreateUserSerializer(serializers.ModelSerializer):
    """Сериализатор для создания нового пользователя."""
    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z',
        max_length=150,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    email = serializers.EmailField(max_length=254,
        validators=[
            UniqueValidator(queryset=User.objects.all())
        ]
    )

    def validate_username(self, username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                "Использовать имя 'me' в качестве username запрещено."
            )
        return username
    

    class Meta:
        model = User
        fields = ('username', 'email',)


class TokenSeializer(serializers.ModelSerializer):
    """Сериализатор для JWT-токена."""
    username = serializers.CharField(required=True)
    confiramtion_code = serializers.CharField(required=True)

    class Meta:
        model = User
        fields = ('username', 'confiramtion_code',)


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
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
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
