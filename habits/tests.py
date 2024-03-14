from datetime import time, datetime, timedelta, timezone, date
from unittest.mock import patch, MagicMock

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from requests import Response
from rest_framework import status

from config import settings
from config.settings import TELEGRAM_ENABLE_TEST_ENDPOINT
from habits.models import Habit
from habits.services import to_utc, tg_send_message
from habits.tasks import habit_reminder, get_now, get_current_day


class TestCRUDHabit(TestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(email='1@1.ru', password='1234')

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

    def test_habit_test_user(self):
        self.client.force_login(self.user)
        url = reverse('habits:habits-test')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['res'], 'Only for superusers')

    @override_settings(TELEGRAM_ENABLE_TEST_ENDPOINT=True)
    def test_habit_test_is_superuser(self):
        self.user.is_superuser = True
        self.user.save()

        self.client.force_login(self.user)
        url = reverse('habits:habits-test')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['res'], 'Endpoint was called')

    @override_settings(TELEGRAM_ENABLE_TEST_ENDPOINT=False)
    def test_habit_test_is_superuser_endpoint_disabled(self):
        self.user.is_superuser = True
        self.user.save()

        self.client.force_login(self.user)
        url = reverse('habits:habits-test')
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['res'], 'Endpoint is disabled')


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


class HabitModelTestCase(TestCase):

    def setUp(self) -> None:
        self.data = {
            "location": "1",
            "time_to_start": "21:51",
            "action": "test",
            "is_pleasant": False,
            "periodic": 0,
            "reward": "test",
            "time_to_complete": 0,
            "is_public": True,
            "owner": None,
            "link_habit": None
        }
        self.habit = Habit.objects.create(**self.data)
        self.habit.save()

    def test_repr(self):
        self.assertEqual(str(self.habit), '"test" в "21:51" в/на "1"')

    def test_clean(self):
        data = self.data.copy()
        data['reward'] = ''
        data['link_habit'] = None
        model = Habit(**data)
        try:
            model.clean()
        except ValidationError as e:
            self.assertEqual(e.args[0], 'Необходимо заполнить либо "Награда", либо "Ссылка на привычку".')
        else:
            self.fail('ValidationError was not raised')


class TelegramTestCase(TestCase):

    def setUp(self) -> None:
        pass

    @patch('requests.post')
    def test_tg_send_message(self, mock_post):
        message = 'Test message'
        chat_id = 'test_chat_id'
        expected_data = {
            'chat_id': chat_id,
            'text': message
        }
        expected_response = MagicMock(spec=Response)
        mock_post.return_value = expected_response

        response = tg_send_message(message, chat_id)
        token = settings.TELEGRAM_BOT_TOKEN
        mock_post.assert_called_once_with(f'https://api.telegram.org/bot{token}/sendMessage', data=expected_data)

        self.assertEqual(response, expected_response)


class TasksTestCase(TestCase):

    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            email='1@1.ru', password='1234', time_zone='UTC+7', telegram_id=123
        )

        data = {
            'location': '1',
            'action': '1',
            'is_pleasant': False,
            'periodic': 0,
            'reward': '1',
            'time_to_complete': 0,
            'owner': self.user,
            'is_public': True,
            'link_habit': None
        }
        self.habit1 = Habit.objects.create(time_to_start=time(10, 15, 00), **data)
        self.habit2 = Habit.objects.create(time_to_start=time(10, 15, 30), **data)
        self.habit3 = Habit.objects.create(time_to_start=time(10, 14, 30), **data)

        self.habit4 = Habit.objects.create(time_to_start=time(10, 14, 29), **data)
        self.habit5 = Habit.objects.create(time_to_start=time(10, 15, 31), **data)

        self.call_count = 0

    @staticmethod
    def mock_time():
        return time(hour=3, minute=15, tzinfo=timezone(timedelta(hours=7)))

    # @staticmethod
    def mock_tg_send_message(self, *args, **kwargs):
        self.call_count += 1

    @patch('habits.tasks.get_current_day')
    @patch('habits.tasks.get_now')
    def test_habit_reminder(
            self,
            mock_now,
            mock_get_current_day,
    ):
        now = self.mock_time()
        time_lag = timedelta(seconds=30)
        tl_plus = (datetime.combine(date.today(), now) + time_lag).time()
        tl_minus = (datetime.combine(date.today(), now) - time_lag).time()

        mock_now.return_value = now, tl_plus, tl_minus
        mock_get_current_day.return_value = 0

        with patch('habits.tasks.tg_send_message', self.mock_tg_send_message):
            habit_reminder()

        self.assertEqual(self.call_count, 3)

    def test_get_now(self):
        now, tl_plus, tl_minus = get_now()
        time_diff = (
                (tl_plus.hour * 3600 + tl_plus.minute * 60 + tl_plus.second) -
                (tl_minus.hour * 3600 + tl_minus.minute * 60 + tl_minus.second)
        )

        self.assertIsInstance(now, datetime)
        self.assertIsInstance(tl_plus, time)
        self.assertIsInstance(tl_minus, time)
        self.assertEqual(time_diff, 60)

    def test_get_current_day(self):
        now = datetime.now(tz=timezone(timedelta(hours=0)))
        current_day1 = get_current_day('UTC+7', now)
        current_day2 = get_current_day('UTC-7', now)

        self.assertEqual(current_day1, 4)
        self.assertEqual(current_day2, 3)
