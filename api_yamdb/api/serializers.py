from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import get_object_or_404
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title
from users.models import User


class UserSerializer(serializers.ModelSerializer):
    """Сеарилизатор для Usera."""
    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z',
                                      max_length=150,
                                      validators=[UniqueValidator(
                                          queryset=User.objects.all())])
    email = serializers.EmailField(max_length=254,
                                   validators=[UniqueValidator(
                                       queryset=User.objects.all())])

    class Meta:
        model = User
        fields = (
            'username', 'email', 'first_name', 'last_name', 'bio', 'role',
        )


class CreateUserSerializer(serializers.Serializer):
    """Сериализатор для создания нового пользователя."""
    username = serializers.RegexField(regex=r'^[\w.@+-]+\Z',
                                      max_length=150,)
    email = serializers.EmailField(max_length=254,)

    def validate_username(self, username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                "Использовать имя 'me' в качестве username запрещено."
            )
        return username

    def validate(self, data):
        username = data.get('username')
        email = data.get('email')
        if (User.objects.filter(username=username).exists()
                and User.objects.get(username=username).email != email):
            raise serializers.ValidationError(
                'Пользователь с таким именем уже зарегистрирован'
            )
        if (User.objects.filter(email=email).exists()
                and User.objects.get(email=email).username != username):
            raise serializers.ValidationError(
                'Пользователь с такой почтой уже зарегистрирован'
            )
        return data


class TokenSeializer(serializers.Serializer):
    """Сериализатор для JWT-токена."""
    username = serializers.CharField(required=True)
    confirmation_code = serializers.CharField(required=True)

    def validate(self, data):
        username = data.get('username')
        if not User.objects.filter(username=username).exists():
            raise NotFound(
                'Пользователь с таким именем не найден.'
            )
        return data


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
    self.action in ('retrieve', 'list').
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
    self.action not in ('retrieve', 'list').
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
    title = serializers.SlugRelatedField(
        slug_field='name',
        read_only=True,
    )
    author = serializers.SlugRelatedField(
        default=serializers.CurrentUserDefault(),
        read_only=True, slug_field='username'
    )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context['view'].kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if request.method == 'POST':
            if Review.objects.filter(title=title, author=author).exists():
                raise ValidationError('Вы не можете добавить более'
                                      'одного отзыва на произведение')
        return data

    class Meta:
        model = Review
        fields = '__all__'


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
