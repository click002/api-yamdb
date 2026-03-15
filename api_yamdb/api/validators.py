import re
from django.core.exceptions import ValidationError


def validate_username_not_me(value):
    """Запрещает использовать 'me' как username."""
    if value.lower() == 'me':
        raise ValidationError(
            'Имя пользователя "me" запрещено.'
        )


def validate_username_chars(value):
    """Проверяет допустимые символы в username."""
    if not re.match(r'^[\w.@+-]+$', value):
        raise ValidationError(
            'Username содержит недопустимые символы.'
        )
