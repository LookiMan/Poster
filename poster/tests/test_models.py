from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils.translation import gettext_lazy as _

from unittest.mock import patch

from .utils import BOT_TOKEN
from .utils import BOT_INFO
from .utils import CHANNEL_ID
from .utils import CHANNEL_INFO

from ..enums import PostTypeEnum
from ..exceptions import BotNotSetException
from ..models import Bot
from ..models import Channel
from ..models import Post


class BotModelTest(TestCase):
    @patch('telegram.bot.TelegramBot.get_me', return_value=BOT_INFO)
    def setUp(self, mocked):
        self.bot = Bot.objects.create(token=BOT_TOKEN)

    def test_creating_bot_without_token(self):
        with self.assertRaises(IntegrityError):
            Bot.objects.create(token=None)

    def test_bot_info(self):
        self.assertEqual(self.bot.token, BOT_TOKEN)
        self.assertEqual(self.bot.bot_id, BOT_INFO.id)
        self.assertEqual(self.bot.first_name, BOT_INFO.first_name)
        self.assertEqual(self.bot.last_name, BOT_INFO.last_name)
        self.assertEqual(self.bot.username, BOT_INFO.username)
        self.assertEqual(self.bot.can_join_groups, BOT_INFO.can_join_groups)

    def test_str_method(self):
        self.assertEqual(str(self.bot), f'@{BOT_INFO.username}')

    def test_verbose_name(self):
        self.assertEqual(Bot._meta.verbose_name, _('Bot'))
        self.assertEqual(Bot._meta.verbose_name_plural, _('Bots'))

    def test_ordering(self):
        self.assertEqual(Bot._meta.ordering, ['-created_at'])


class ChannelModelTest(TestCase):
    @patch('telegram.bot.TelegramBot.get_me', return_value=BOT_INFO)
    @patch('telegram.bot.TelegramBot.get_channel_info', return_value=CHANNEL_INFO)
    def setUp(self, *mocked):
        self.bot = Bot.objects.create(token=BOT_TOKEN)
        self.channel = Channel.objects.create(
            bot=self.bot,
            channel_id=CHANNEL_ID
        )

    def test_creating_channel_without_channel_id(self):
        with self.assertRaises(IntegrityError):
            Channel.objects.create(
                bot=self.bot,
                channel_id=None
            )

    def test_creating_channel_without_bot(self):
        with self.assertRaises(BotNotSetException):
            Channel.objects.create(
                bot=None,
                channel_id=CHANNEL_ID
            )

    def test_channel_info(self):
        self.assertEqual(self.channel.channel_id, CHANNEL_ID)
        self.assertEqual(self.channel.bot_id, self.bot.id)
        self.assertEqual(self.channel.title, CHANNEL_INFO.title)
        self.assertEqual(self.channel.description, CHANNEL_INFO.description)
        self.assertEqual(self.channel.username, CHANNEL_INFO.username)
        self.assertEqual(self.channel.invite_link, CHANNEL_INFO.invite_link)

    def test_str_method(self):
        self.assertEqual(str(self.channel), f'Telegram channel: {CHANNEL_INFO.title}')

    def test_verbose_name(self):
        self.assertEqual(Channel._meta.verbose_name, _('Channel'))
        self.assertEqual(Channel._meta.verbose_name_plural, _('Channels'))

    def test_ordering(self):
        self.assertEqual(Channel._meta.ordering, ['-created_at'])


class PostModelTest(TestCase):
    def test_creating_post_without_required_field_post_type(self):
        with self.assertRaises(IntegrityError):
            Post.objects.create(post_type=None)

    def test_creating_post_empty(self):
        post = Post.objects.create(post_type=PostTypeEnum.TEXT)

        self.assertIsNone(post.document.name)
        self.assertIsNone(post.caption)
        self.assertListEqual(list(post.gallery_documents.all()), [])
        self.assertListEqual(list(post.gallery_photos.all()), [])
        self.assertIsNone(post.message)
        self.assertIsNone(post.photo.name)
        self.assertIsNone(post.video.name)
        self.assertIsNone(post.voice.name)

    def test_is_media_gallery(self):
        post = Post.objects.create(post_type=PostTypeEnum.TEXT)
        self.assertFalse(post.is_media_gallery)

        post = Post.objects.create(post_type=PostTypeEnum.GALLERY_DOCUMENTS)
        self.assertTrue(post.is_media_gallery)

        post = Post.objects.create(post_type=PostTypeEnum.GALLERY_PHOTOS)
        self.assertTrue(post.is_media_gallery)

    def test_str_method(self):
        post = Post.objects.create(post_type=PostTypeEnum.TEXT)
        self.assertEqual(str(post), f'{post.post_type} post with id {post.id}')

    def test_verbose_name(self):
        self.assertEqual(Post._meta.verbose_name, _('Post'))
        self.assertEqual(Post._meta.verbose_name_plural, _('Posts'))

    def test_ordering(self):
        self.assertEqual(Post._meta.ordering, ['-updated_at'])
