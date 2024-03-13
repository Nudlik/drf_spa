from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from users.validators import check_time_zone


class TestValidators(TestCase):

    def setUp(self) -> None:
        pass

    def test_check_time_zone(self):
        data_good = [
            'UTC-12', 'UTC-11', 'UTC-10', 'UTC-9:30', 'UTC-9', 'UTC-8', 'UTC-7', 'UTC-6', 'UTC-5', 'UTC-4', 'UTC-3:30',
            'UTC-3', 'UTC-2', 'UTC-1', 'UTC+0', 'UTC+1', 'UTC+2', 'UTC+3', 'UTC+3:30', 'UTC+4', 'UTC+4:30', 'UTC+5',
            'UTC+5:30', 'UTC+5:45', 'UTC+6', 'UTC+6:30', 'UTC+7', 'UTC+8', 'UTC+8:45', 'UTC+9', 'UTC+9:30', 'UTC+10',
            'UTC+10:30', 'UTC+11', 'UTC+12', 'UTC+12:45', 'UTC+13', 'UTC+14'
        ]
        for utc in data_good:
            self.assertIsNone(check_time_zone(utc))

    def test_check_time_zone_bad(self):
        data_bad = [
            'МСК+1', 'МСК+2', 'МСК+3', 'ROW+4', 'МСК+5', 'МСК+6', 'МСК+7', 'МСК+8', 'МСК+9', 'МСК+10',
        ]
        for utc in data_bad:
            self.assertRaises(ValidationError, check_time_zone, utc)


class UsersTestCase(TestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email='1@1.ru', password='1234')
        self.user2 = get_user_model().objects.create_user(email='2@2.ru', password='1234')
        self.user.save()

    def test_create_allow_any(self):
        data = {
            'email': '11@1.ru',
            'password': 'test',
        }
        url = reverse('users:users-list')
        response = self.client.post(url, data, 'application/json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_view_users_no_auth(self):
        url = reverse('users:users-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete(self):
        self.client.force_login(self.user2)
        url = reverse('users:users-detail', args=[self.user.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_login(self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_update(self):
        self.client.force_login(self.user)
        url = reverse('users:users-detail', args=[self.user.id])
        data = {
            'password': 'test',
            'telegram_id': 123,
        }
        response = self.client.patch(url, data, 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_user_auth_jwt(self):
        url = reverse('users:token_obtain_pair')
        data = {
            'email': '1@1.ru',
            'password': '1234',
        }
        response = self.client.post(url, data, 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        token = response.data['refresh']
        data = {'refresh': token}
        url = reverse('users:token_refresh')
        response = self.client.post(url, data, 'application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser('11@1.ru', '1234')
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)

    def test_create_superuser_with_invalid_is_staff(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser('11@1.ru', is_staff=False)

    def test_create_superuser_with_invalid_is_superuser(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser('11@1.ru', is_superuser=False)

    def test_create_superuser_with_invalid__create_user(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(None)
