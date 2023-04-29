from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.db.models import Avg
from django.conf import settings
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import User
from reviews.models import Category, Genre, Review, Title
from .filters import TitlesFilter
from .mixins import ListCreateDestroyViewSet
from .permissions import (
    IsAdminOnly, IsAdminOrReadOnly, IsAuthorAdminModeratorPermission
)
from .serializers import (
    UserSerializer, CreateUserSerializer, TokenSeializer,
    CategorySerializer, GenreSerializer,
    ReadOnlyTitleSerializer, TitleCreateSerializer,
    ReviewSerializer, CommentSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def get_jwt_token(request):
    serializer = TokenSeializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    username = serializer.validated_data.get('username')
    confirmation_code = serializer.validated_data.get('confirmation_code')
    user = get_object_or_404(User, username=username)
    if default_token_generator.check_token(user, confirmation_code):
        refresh = RefreshToken.for_user(user)
        return Response(
            {'token': str(refresh.access_token)},
            status=status.HTTP_200_OK)
    return Response(
        {'confirmation_code': 'Код подтверждения неверен'},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
@permission_classes([AllowAny])
def send_confirmation_code(request):
    serializer = CreateUserSerializer(data=request.data)
    # if serializer.is_valid():
    #     user = serializer.save()
    #     confirmation_code = default_token_generator.make_token(user)
    #     message = f'Код подтверждения {confirmation_code}'
    #     subject = 'Код подтверждения'
    #     send_mail(subject, message,
    #         from_email=None,
    #         recipient_list=[user.email],
    #     )
    #     return Response(
    #         serializer.data, status=status.HTTP_200_OK
    #     )
    # return Response(status=status.HTTP_400_BAD_REQUEST)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    user = get_object_or_404(
        User,
        username=serializer.validated_data['username']
    )
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Код подтверждения',
        message=f'Код подтверждения: {confirmation_code}',
        from_email=None,
        recipient_list=[user.email],
    )

    return Response(serializer.data, status=status.HTTP_200_OK)


class UsersViewSet(viewsets.ModelViewSet):
    """Вьюсет для User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated], url_path='me')
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        if request.method == 'PATCH':
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save(role=user.role, partial=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


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
    queryset = Title.objects.all().annotate(
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


class ReviewViewSet(viewsets.ModelViewSet):
    """
    Обрабатывает запросы к эндпоинтам
    отзывов.
    """
    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorAdminModeratorPermission,)

    def get_queryset(self):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, pk=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """
    Обрабатывает запросы к эндпоинтам
    комментариев к отзывам.
    """
    serializer_class = CommentSerializer
    permission_classes = (IsAuthorAdminModeratorPermission,)

    def get_queryset(self):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, pk=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
