from django.forms import ValidationError
from django.test import TestCase

from telebot.apihelper import ApiTelegramException

from unittest.mock import patch

from poster.forms import BotAdminForm


class BotAdminFormTestCase(TestCase):

    @patch('telegram.bot.TelegramBot.get_me')
    def test_valid_token(self, mocked):
        def get_me():
            pass

        mocked.side_effect = get_me

        form_data = {
            'token': '0123456789:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
        }
        form = BotAdminForm(data=form_data)

        self.assertTrue(form.is_valid())

    @patch('telegram.bot.TelegramBot.get_me')
    def test_invalid_token(self, mocked):
        def get_me():
            raise ApiTelegramException(
                function_name='tets',
                result="{'error_code': 400, 'description': 'Invalid Token'}",
                result_json={'error_code': 400, 'description': 'Invalid Token'}
            )

        mocked.side_effect = get_me

        form_data = {
            'token': 'INVALID_TOKEN:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX',
        }
        form = BotAdminForm(data=form_data)

        self.assertFalse(form.is_valid())

        with self.assertRaises(ValidationError):
            form.clean()

    @patch('telegram.bot.TelegramBot.get_me')
    def test_missing_token(self, mocked):
        def get_me():
            pass

        mocked.side_effect = get_me

        form_data = {
            'token': None,
        }
        form = BotAdminForm(data=form_data)

        self.assertFalse(form.is_valid())
        self.assertIn('token', form.errors)
