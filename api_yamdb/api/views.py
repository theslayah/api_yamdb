from django.db.models import Avg
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets

from reviews.models import Category, Genre, Title
from .filters import TitlesFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import (IsAdmin, IsAdminOrReadOnly,
                          IsAdminModeratorOwnerOrReadOnly)
from .serializers import (CategorySerializer, GenreSerializer,
                          ReadOnlyTitleSerializer,
                          TitleCreateSerializer)


class CategoryViewSet(ListCreateDestroyViewSet):
    """Обрабатывает запросы к эндпоинтам r'categories'."""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class GenreViewSet(ListCreateDestroyViewSet):
    """Обрабатывает запросы к эндпоинтам r'genres'."""
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ("name",)
    lookup_field = "slug"


class TitleViewSet(viewsets.ModelViewSet):
    """Обрабатывает запросы к эндпоинтам r'titles'."""
    queryset = Title.objects.annotate(
        rating=Avg("reviews__score")
    ).order_by("name")
    serializer_class = TitleCreateSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = TitlesFilter

    def get_serializer_class(self):
        if self.action in ("retrieve", "list"):
            return ReadOnlyTitleSerializer
        return TitleCreateSerializer
