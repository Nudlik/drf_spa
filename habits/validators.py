from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


def validate_time_to_complete(time_to_complete: int) -> None:
    """ Время выполнения приятной привычки должно быть не больше 120 секунд. """

    if time_to_complete > 120:
        raise ValidationError(
            _(f'Время выполнения приятной привычки должно быть не больше 120 секунд,'
              f'сейчас время на выполнения {time_to_complete} секунд'),
            params={'time_to_complete': time_to_complete},
        )
