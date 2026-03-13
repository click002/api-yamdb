from django.contrib.auth import get_user_model
from rest_framework import serializers

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        """Запрещаем использовать username 'me'(согласно postman_collection)"""
        if value.lower() == 'me':
            raise serializers.ValidationError(
                'Имя пользователя "me" запрещено.'
            )
        return value


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()
