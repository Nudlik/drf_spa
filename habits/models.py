from django.contrib.auth import get_user_model
from django.db import models

from habits.validators import validate_time_to_complete
from utils.const import NULLABLE


class Habit(models.Model):

    class PERIODIC(models.IntegerChoices):
        DAILY = 0, 'Ежедневно'
        WEEKLY = 1, 'Еженедельно'

    owner = models.ForeignKey(
        to=get_user_model(),
        on_delete=models.SET_NULL,
        **NULLABLE,
        related_name='habit',
        verbose_name='Владелец'
    )
    location = models.CharField(max_length=255, verbose_name='Местоположение')
    time_to_start = models.TimeField(verbose_name='Начало')
    action = models.CharField(max_length=255, verbose_name='Действие')
    is_pleasant = models.BooleanField(verbose_name='Приятная ли это привычка?')
    link_habit = models.ForeignKey(
        to='self',
        on_delete=models.SET_NULL,
        **NULLABLE,
        related_name='link_habits',
        verbose_name='Ссылка на привычку',
    )
    periodic = models.IntegerField(choices=PERIODIC.choices, default=PERIODIC.DAILY, verbose_name='Периодичность')
    reward = models.CharField(max_length=255, **NULLABLE, verbose_name='Награда')
    time_to_complete = models.IntegerField(validators=[validate_time_to_complete], verbose_name='Время на выполнение')
    is_public = models.BooleanField(verbose_name='Публичная ли привычка?')

    class Meta:
        verbose_name = 'Привычка'
        verbose_name_plural = 'Привычки'
        ordering = ['id']

    def __str__(self):
        return f'Я буду {self.action} в {self.time_to_start} в/на {self.location}'
