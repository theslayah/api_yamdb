from rest_framework import serializers
from reviews.models import Category, Genre, Title

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
