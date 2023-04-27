from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UsersViewSet, send_confirmation_code, get_jwt_token,
    CategoryViewSet, GenreViewSet, TitleViewSet,
)

router = DefaultRouter
router.register(r'users', UsersViewSet)


urlpatterns = [
    path('v1/auth/token/', get_jwt_token.as_view(), name='token_obtain'),
    path('v1/auth/signup/', send_confirmation_code.as_view(), name='sign_up'),
]
