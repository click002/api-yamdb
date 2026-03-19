import re
from django.core.exceptions import ValidationError
from django.utils import timezone


FORBIDDEN_USERNAME = 'me'
USERNAME_CHARS = r'^[\w.@+-]+$'


def doc(docstring):
    """Декоратор для задания docstring динамически."""
    def decorator(func):
        func.__doc__ = docstring
        return func
    return decorator

#  вместо """"Запрещает использовать 'me' как username.""" теперь декоратор
@doc(f"Запрещает использовать '{FORBIDDEN_USERNAME}' как username.")
def validate_username_not_me(value):
    if value == FORBIDDEN_USERNAME:
        raise ValidationError(
            f'Имя пользователя "{FORBIDDEN_USERNAME}" запрещено.'
        )


def validate_username_chars(value):
    """Проверяет допустимые символы в username."""
    if not re.match(USERNAME_CHARS, value):
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
