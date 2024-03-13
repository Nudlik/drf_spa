from datetime import time

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from habits.models import Habit
from habits.services import to_utc


class TestCRUDHabit(TestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email='1@1.ru', password='1234')
        self.user.save()

        self.data = {
            "location": "1",
            "time_to_start": "21:51",
            "action": "чихнуть1",
            "is_pleasant": False,
            "periodic": 0,
            "reward": "сказать будь здоров",
            "time_to_complete": 120,
            "is_public": True,
            "owner": None,
            "link_habit": None
        }

        copy_data = self.data.copy()
        copy_data['is_pleasant'] = True
        self.habit_no_is_pleasant = Habit.objects.create(**copy_data)
        self.habit_no_is_pleasant.save()
        self.count_habits = Habit.objects.count()

    def test_create_good(self):
        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), self.count_habits + 1)

    def test_create_habits_is_pleasant(self):
        self.data['is_pleasant'] = True
        self.data['reward'] = ''
        self.data['link_habit'] = None

        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), self.count_habits + 1)

    def test_create_habits_no_is_pleasant_and_reward(self):
        self.data['is_pleasant'] = False
        self.data['reward'] = '123'
        self.data['link_habit'] = None

        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), self.count_habits + 1)

    def test_create_habits_no_is_pleasant_and_link_habit(self):
        self.data['is_pleasant'] = False
        self.data['reward'] = ''
        self.data['link_habit'] = self.habit_no_is_pleasant.id

        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), self.count_habits + 1)

    def test_create_link_habit_no_is_pleasant(self):
        self.data['is_pleasant'] = False
        self.data['reward'] = ''
        self.data['link_habit'] = self.habit_no_is_pleasant.id

        self.habit_no_is_pleasant.is_pleasant = False
        self.habit_no_is_pleasant.save()

        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Habit.objects.count(), self.count_habits)

    def test_create_validator_is_pleasant_and_no_reward(self):
        self.data['is_pleasant'] = True

        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'][0],
            'У приятной привычки не может быть вознаграждения или связанной привычки.'
        )
        self.assertEqual(Habit.objects.count(), self.count_habits)

    def test_create_no_reward_and_no_link_habit(self):
        self.data['reward'] = ''
        self.data['link_habit'] = None

        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'][0],
            'Необходимо заполнить либо "Награда", либо "Ссылка на привычку".'
        )
        self.assertEqual(Habit.objects.count(), self.count_habits)

    def test_create_reward_and_link_habit(self):
        self.data['reward'] = '123'
        self.data['link_habit'] = self.habit_no_is_pleasant.id

        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'][0],
            'Должно быть заполнено только одно из полей "Награда" или "Ссылка на привычку".'
        )
        self.assertEqual(Habit.objects.count(), self.count_habits)

    def test_create_is_pleasant_and_reward_or_link_habit(self):
        self.data['is_pleasant'] = True
        self.data['reward'] = '123'
        self.data['link_habit'] = self.habit_no_is_pleasant.id

        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['non_field_errors'][0],
            'У приятной привычки не может быть вознаграждения или связанной привычки.'
        )
        self.assertEqual(Habit.objects.count(), self.count_habits)

    def test_create_time_to_complete(self):
        self.data['time_to_complete'] = 121

        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['time_to_complete'][0],
            'Время выполнения приятной привычки должно быть не больше 120 секунд,сейчас время на выполнения 121 секунд'
        )
        self.assertEqual(Habit.objects.count(), self.count_habits)

    def test_create_save_owner(self):
        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), self.count_habits + 1)
        self.assertEqual(Habit.objects.last().owner, self.user)
        self.assertEqual(response.data['owner'], self.user.id)

    def test_published_endpoint(self):
        self.client.force_login(self.user)
        url = reverse('habits:habits-published')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), self.count_habits)

    def test_published_endpoint_page_is_None(self):
        Habit.objects.all().delete()

        self.client.force_login(self.user)
        url = reverse('habits:habits-published')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['results'], [])

        next_url = response.data['next']
        next_response = self.client.get(next_url)
        self.assertEqual(next_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_habit_queryset(self):
        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)

        self.data['owner'] = self.user
        Habit.objects.create(**self.data)
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['owner'], self.user.id)


class ServiceTestCase(TestCase):

    def setUp(self) -> None:
        pass

    def test_to_utc_positive_offset(self):
        """ Проверяем, что функция корректно преобразует время в UTC для положительного сдвига """

        result = to_utc(time(10, 30), 'UTC+3')
        self.assertEqual(result, time(7, 30))

    def test_to_utc_negative_offset(self):
        """ Проверяем, что функция корректно преобразует время в UTC для отрицательного сдвига """

        result = to_utc(time(10, 30), 'UTC-5')
        self.assertEqual(result, time(15, 30))

    def test_to_utc_zero_offset(self):
        """ Проверяем, что функция корректно обрабатывает нулевой сдвиг """

        result = to_utc(time(10, 30), 'UTC-0')
        self.assertEqual(result, time(10, 30))

    def test_to_utc_crossing_midnight(self):
        """ Проверяем, что функция корректно обрабатывает переход через полночь """

        result = to_utc(time(3, 30), 'UTC+4')
        self.assertEqual(result, time(23, 30))

    def test_to_utc_negative_minute(self):
        """ Проверяем, что функция корректно обрабатывает случай, когда минуты отрицательны """

        result = to_utc(time(1, 30), 'UTC+2:30')
        self.assertEqual(result, time(23, 00))

    def test_to_utc_positive_minute(self):
        """ Проверяем, что функция корректно обрабатывает случай, когда минуты положительны """

        result = to_utc(time(23, 30), 'UTC-2:30')
        self.assertEqual(result, time(2, 00))

    def test_to_utc_negative_minute_adjustment(self):
        """ Проверяем, что функция корректно обрабатывает случай, когда минуты отрицательны и происходит коррекция """

        result = to_utc(time(1, 0), 'UTC+2:30')
        self.assertEqual(result, time(22, 30))
