from datetime import timedelta, datetime, timezone

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db.models import Q

from habits.models import Habit
from habits.services import tg_send_message, to_utc, get_user_timezone_diff


@shared_task
def habit_reminder():
    time_lag = timedelta(seconds=30)
    now = datetime.now(tz=timezone(timedelta(hours=0)))
    tl_plus = (now + time_lag).time()
    tl_minus = (now - time_lag).time()

    # мок
    # from datetime import time, date
    # now = time(hour=3, minute=15, tzinfo=timezone(timedelta(hours=7)))
    # tl_plus = (datetime.combine(date.today(), now) + time_lag).time()
    # tl_minus = (datetime.combine(date.today(), now) - time_lag).time()

    users = get_user_model().objects.filter(
        telegram_id__isnull=False,
        is_active=True,
        time_zone__isnull=False
    ).prefetch_related('habit')

    for user in users:
        h, m = get_user_timezone_diff(user.time_zone)
        tz_time = now.astimezone(timezone(timedelta(hours=h, minutes=m)))
        is_day = tz_time.weekday() + 1
        for habit in user.habit.filter(Q(periodic=is_day) | Q(periodic=Habit.PERIODIC.DAILY)):
            tu = to_utc(habit.time_to_start, user.time_zone)
            if tl_minus <= tu <= tl_plus:
                tg_send_message(
                    message=str(habit),
                    chat_id=user.telegram_id
                )
