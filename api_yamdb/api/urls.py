from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    UsersViewSet, send_confirmation_code, get_jwt_token,
    CategoryViewSet, GenreViewSet, TitleViewSet,
)

router = DefaultRouter()
router.register(r'users', UsersViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(r'titles', TitleViewSet)

urlpatterns = [
    path('v1/auth/token/', get_jwt_token, name='token_obtain'),
    path('v1/auth/signup/', send_confirmation_code, name='sign_up'),
    path('v1/', include(router.urls)),
]
