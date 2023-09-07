from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _
from telebot.types import User
from unittest.mock import patch

from ..models import Bot


BOT_TOKEN = '01234567890:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'

bot_info = User.de_json({
    'id': 1234567890,
    'is_bot': True,
    'first_name': 'test_bot_1_first_name',
    'username': 'test_fff_test_bot',
    'last_name': None,
    'language_code': None,
    'can_join_groups': True,
    'can_read_all_group_messages': False,
    'supports_inline_queries': False,
    'is_premium': None,
    'added_to_attachment_menu': None,
})


class BotModelTest(TestCase):
    @patch('telegram.bot.TelegramBot.get_me', return_value=bot_info)
    def setUp(self, mocked):
        self.bot = Bot.objects.create(token=BOT_TOKEN)

    def test_creating_bot_without_token(self):
        with self.assertRaises(IntegrityError):
            Bot.objects.create(token=None)

    def test_bot_info(self):
        self.assertEqual(self.bot.token, BOT_TOKEN)
        self.assertEqual(self.bot.bot_id, bot_info.id)
        self.assertEqual(self.bot.first_name, bot_info.first_name)
        self.assertEqual(self.bot.last_name, bot_info.last_name)
        self.assertEqual(self.bot.username, bot_info.username)
        self.assertEqual(self.bot.can_join_groups, bot_info.can_join_groups)

    def test_str_method(self):
        self.assertEqual(str(self.bot), f'@{bot_info.username}')

    def test_verbose_name(self):
        self.assertEqual(Bot._meta.verbose_name, _('Bot'))
        self.assertEqual(Bot._meta.verbose_name_plural, _('Bots'))

    def test_ordering(self):
        self.assertEqual(Bot._meta.ordering, ['-created_at'])
