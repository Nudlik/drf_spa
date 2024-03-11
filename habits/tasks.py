from datetime import timedelta, datetime, timezone

from celery import shared_task
from django.contrib.auth import get_user_model

from habits.services import tg_send_message, to_utc


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
        for habit in user.habit.all():
            tu = to_utc(habit.time_to_start, user.time_zone)
            if tl_minus <= tu <= tl_plus:
                tg_send_message(
                    message=str(habit),
                    chat_id=user.telegram_id
                )
