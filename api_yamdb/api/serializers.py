from rest_framework import serializers
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


class TokenSeializer(serializers.ModelSerializerd):
    """Сериализатор для JWT-токена."""
    username = serializers.CharField()
    confiramtion_code = serializers.CharField()

    class Meta:
        model = User
        fields = ('username', 'confirmation_codde',)
