from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status


class TestCrudHabit(TestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email='1@1.ru', password='1234')

        self.user.save()

    def test_create_validator_is_pleasant_and_no_reward(self):
        data = {
            "location": "1",
            "time_to_start": "21:51",
            "action": "чихнуть1",
            "is_pleasant": True,
            "periodic": 0,
            "reward": "сказать будь здоров",
            "time_to_complete": 120,
            "is_public": True,
            "owner": None,
            "link_habit": None
        }
        self.client.force_login(self.user)
        url = reverse('habits:habits-list')
        response = self.client.post(url, data, 'application/json')
        print(response.status_code)
        print(response.data)
        print(response)
        # self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

