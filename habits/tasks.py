from datetime import timedelta, datetime, timezone

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Q

from habits.models import Habit
from habits.services import tg_send_message, to_utc, get_user_timezone_diff


def get_now():
    now = datetime.now(tz=timezone(timedelta(hours=0)))
    time_lag = timedelta(seconds=30)
    tl_plus = (now + time_lag).time()
    tl_minus = (now - time_lag).time()
    return now, tl_plus, tl_minus


def get_current_day(user_timezone, now):
    h, m = get_user_timezone_diff(user_timezone)
    tz_time = now.astimezone(timezone(timedelta(hours=h, minutes=m)))
    day = tz_time.weekday() + 1
    return day


@shared_task
def habit_reminder():
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
                tg_send_message(
                    message=str(habit),
                    chat_id=user.telegram_id
                )
