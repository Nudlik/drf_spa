from django.core.exceptions import ValidationError
from django.test import TestCase

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
