from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings

from rest_framework import status, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

from users.models import User
from .permissions import (
    IsAdminOnly, IsAdminOrReadOnly, IsAuthorAdminModeratorPermission
)
from .serializers import (
    UserSerializer, CreateUserSerializer, TokenSeializer
)


@api_view(['POST'])
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
            status=status.HTTP_200_OK
        )
    return Response(
        {'confirmation_code': 'Код подтверждения неверен'},
        status=status.HTTP_400_BAD_REQUEST
    )


@api_view(['POST'])
def send_confirmation_code(request):
    serializer = CreateUserSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    email = serializer.validated_data.get('email')
    username = serializer.validated_data.get('username')
    if (
        User.objects.filter(username=username).exists() or
        User.objects.filter(email=email).exists()
    ):
        return Response(
            {'Username или Email уже используется.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    else:
        User.objects.create_user(username=username, email=email)
    user = get_object_or_404(User, email=email)
    confirmation_code = default_token_generator.make_token(user)
    message = f'Код подтверждения {confirmation_code}'
    subject = 'Код подтверждения'
    send_mail(subject, message, settings.EMAIL_TOKEN, [email])
    return Response(
        serializer.data, status=status.HTTP_200_OK
    )


class UsersViewSet(viewsets.ModelViewSet):
    """Вьюсет для User."""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOnly,)
    lookup_field = 'username'

    @action(detail=False, methods=['get', 'patch'],
            permission_classes=[IsAuthenticated], url_path='me')
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save(role=user.role, partial=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
