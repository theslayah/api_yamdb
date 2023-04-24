from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Создание пользователя."""
    ADMIN = 'admin'
    MODERATOR = 'moderator'
    USER = 'user'

    ROLES = [
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    ]
    email = models.EmailField(
        max_length=254,
        unique=True,
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    role = models.CharField(
        verbose_name='Роль',
        max_length=9,
        choices=ROLES,
        default='user',
    )
    confirmation_code = models.CharField(
        verbose_name='Токен',
        max_length=15,
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('username',)

    @property
    def is_admin(self):
        """Проверка наличия прав администратора."""
        return self.role == self.ADMIN or self.is_superuser

    @property
    def is_moderator(self):
        """Проверка наличия прав модератора."""
        return self.role == self.MODERATOR

    @property
    def is_user(self):
        """Проверка наличия стандартных прав."""
        return self.role == self.USER

    def __str__(self):
        return self.username
