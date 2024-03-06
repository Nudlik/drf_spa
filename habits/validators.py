from typing import TYPE_CHECKING, TypeVar

from django.core.exceptions import ValidationError
from django.db.models import Model
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext_lazy as _

if TYPE_CHECKING:
    from habits.models import Habit
    T = TypeVar('T', bound=Habit)
else:
    T = Model


def validate_time_to_complete(time_to_complete: int) -> None:
    """ Время выполнения приятной привычки должно быть не больше 120 секунд. """

    if time_to_complete > 120:
        raise ValidationError(
            _(f'Время выполнения приятной привычки должно быть не больше 120 секунд,'
              f'сейчас время на выполнения {time_to_complete} секунд'),
            params={'time_to_complete': time_to_complete},
        )


class CheckLinkAndReward:
    """
    Исключить одновременный выбор связанной привычки и указания вознаграждения.
    В модели не должно быть заполнено одновременно и поле вознаграждения, и поле связанной привычки.
    Можно заполнить только одно из двух полей.
    """

    def __init__(self, link_habit: str, reward: str) -> None:
        self.link_habit = link_habit
        self.reward = reward

    def __call__(self, data: T) -> None:

        link_habit: T = getattr(data, self.link_habit)
        link_habit_vb: str = data._meta.get_field(self.link_habit).verbose_name

        reward: T = getattr(data, self.reward)
        reward_vb: str = data._meta.get_field(self.reward).verbose_name

        if not data.is_pleasant:
            if reward and link_habit:
                raise ValidationError(f'Должно быть заполнено только одно из полей "{_(reward_vb)}" '
                                      f'или «{_(link_habit_vb)}».')

            if not reward and not link_habit:
                raise ValidationError(f'Необходимо заполнить либо "{_(reward_vb)}", либо "{_(link_habit_vb)}".')

        # У приятной привычки не может быть вознаграждения или связанной привычки.
        elif reward or link_habit:
            raise ValidationError(
                _('У приятной привычки не может быть вознаграждения или связанной привычки.')
            )


def validate_link_habit_is_pleasant(link_habit_id: int) -> None:
    """ В связанные привычки могут попадать только привычки с признаком приятной привычки. """

    from habits.models import Habit

    link_habit = get_object_or_404(Habit, id=link_habit_id)
    if not link_habit.is_pleasant:
        raise ValidationError(
            _('В связанные привычки могут попадать только привычки с признаком приятной привычки.'),
        )
