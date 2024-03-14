from datetime import timedelta, datetime, timezone, time

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Q

from habits.models import Habit
from habits.services import tg_send_message, to_utc, get_user_timezone_diff, get_message


def get_now() -> (datetime, time, time):
    """ Получаем текущую дату в UTC+0 и время погрешности для выборки уведомлений """

    now = datetime.now(tz=timezone(timedelta(hours=0)))
    time_lag = timedelta(seconds=30)
    tl_plus = (now + time_lag).time()
    tl_minus = (now - time_lag).time()
    return now, tl_plus, tl_minus


def get_current_day(user_timezone: str, now: datetime) -> int:
    """ Получаем текущий день недели с учетом часового пояса пользователя """

    h, m = get_user_timezone_diff(user_timezone)
    tz_time = now.astimezone(timezone(timedelta(hours=h, minutes=m)))
    day = tz_time.weekday() + 1
    return day


@shared_task
def habit_reminder() -> None:
    """ Напоминания о привычках, рассылка в тг """

    now, tl_plus, tl_minus = get_now()

    users = get_user_model().objects.filter(
        telegram_id__isnull=False,
        is_active=True,
        time_zone__isnull=False
    ).prefetch_related('habit')

    for user in users:
        current_day = get_current_day(user.time_zone, now)
        habits = user.habit.filter(Q(periodic=current_day) | Q(periodic=Habit.PERIODIC.DAILY))
        for habit in habits:
            tu = to_utc(habit.time_to_start, user.time_zone)
            if tl_minus <= tu <= tl_plus:
                message = get_message(habit)
                tg_send_message(
                    message=message,
                    chat_id=user.telegram_id
                )
