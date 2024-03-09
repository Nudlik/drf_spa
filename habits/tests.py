from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from habits.models import Habit


class TestCrudHabit(TestCase):

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

    def test_create_good(self):
        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, self.data, 'application/json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Habit.objects.count(), self.count_habits + 1)

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
