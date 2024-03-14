import re

from django.core.exceptions import ValidationError


def check_time_zone(time_zone: str) -> None:
    """ Проверяем правильно ли ввел пользователь часовой пояс """

    regex = r'^((UTC)[+-]((1[0-4])|\d)(\:(30|45))?)$'
    if not re.match(regex, time_zone):
        raise ValidationError('Недопустимый часовой пояс')
