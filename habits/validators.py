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


class CheckLinkAndReward:
    """
    Исключить одновременный выбор связанной привычки и указания вознаграждения.
    В модели не должно быть заполнено одновременно и поле вознаграждения, и поле связанной привычки.
    Можно заполнить только одно из двух полей.
    """

    def __init__(self, link_habit, reward):
        self.link_habit = link_habit
        self.reward = reward

    def __call__(self, data):
        link_habit, link_habit_vb = getattr(data, self.link_habit), data._meta.get_field(self.link_habit).verbose_name
        reward, reward_vb = getattr(data, self.reward), data._meta.get_field(self.reward).verbose_name

        if reward and link_habit:
            raise ValidationError(f'Должно быть заполнено только одно из полей "{_(reward_vb)}" '
                                  f'или «{_(link_habit_vb)}».')

        if not reward and not link_habit:
            raise ValidationError(f'Необходимо заполнить либо "{_(reward_vb)}", либо "{_(link_habit_vb)}".')
