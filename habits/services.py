from datetime import time

import requests
from requests import Response

from config.settings import TELEGRAM_BOT_TOKEN
from habits.models import Habit


def tg_send_message(message: str, chat_id: str | int) -> Response | None:
    """ Отправка сообщения в телеграм. """

    url = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage'
    data = {
        'chat_id': chat_id,
        'text': message
    }
    response = requests.post(url, data=data)
    return response


def get_user_timezone_diff(utc_time: str) -> tuple[int, int]:
    """ Получаем разницу часового пояса пользователя. """

    sign = -1 if utc_time[3] == '-' else 1
    hours, minutes = utc_time[4:].split(':') if utc_time.count(':') == 1 else (utc_time[4:], 0)
    return int(hours) * sign, int(minutes) * sign


def to_utc(t: time, offset: str) -> time:
    """ Конвертируем время в UTC. """

    offset_h, offset_m = get_user_timezone_diff(offset)

    h = t.hour - offset_h
    m = t.minute - offset_m

    if m < 0:
        h, m = h - 1, m + 60
    elif m >= 60:
        h, m = h + 1, m - 60

    if h < 0:
        h += 24
    elif h >= 24:
        h -= 24

    return time(h, m)


def get_message(habit: Habit) -> str:
    """ Составляем сообщение. """

    msg = f'Выполнить: "{habit.action}" в "{habit.time_to_start}" в/на "{habit.location}"'
    if habit.link_habit:
        reward = f'В награду выполнить приятную привычку: "{habit.link_habit.action}"'
    else:
        reward = f'В награду получить: "{habit.reward}"'
    time_to_complete = f'Время на выполнения приятностей: "{habit.time_to_complete} сек."'

    return '\n'.join([msg, reward, time_to_complete])
