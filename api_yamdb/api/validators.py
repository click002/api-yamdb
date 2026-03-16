import re
from django.core.exceptions import ValidationError
from django.utils import timezone


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


def validate_year(value):
    """Проверяет, что год не больше текущего."""
    current_year = timezone.now().year
    if value > current_year:
        raise ValidationError(
            f'Год выпуска {value} не может быть больше текущего {current_year}'
        )
    return value
