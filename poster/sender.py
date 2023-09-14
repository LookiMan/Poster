from abc import abstractmethod
from abc import ABC
from typing import Any
from typing import List
from io import BytesIO
from os import path
from os import getenv

from django.db.models import QuerySet
from discord import SyncWebhookMessage as DiscordMessage
from requests.exceptions import RequestException
from telebot.apihelper import ApiTelegramException
from telebot.types import Message as TelegramMessage
from telebot.types import InputMediaDocument
from telebot.types import InputMediaPhoto

from .enums import MessengerEnum
from .exceptions import SenderNotFound
from .exceptions import UnknownPostType
from .models import Bot
from .models import Channel
from .models import GalleryDocument
from .models import GalleryPhoto
from .models import Post
from .utils import escape_discord_message
from .utils import escape_telegram_message

from discord_bot import DiscordBot
from telegram_bot import TelegramBot

import logging
logger = logging.getLogger(__name__)


class AbstractSender(ABC):
    @abstractmethod
    def delete_message(self, channel_id: int, message_id: int, **kwargs) -> dict:
        pass

    @abstractmethod
    def edit_message(self, channel_id: int, message_id: int, post: Post, **kwargs) -> DiscordMessage | TelegramMessage:  # NOQA: E501
        pass

    @abstractmethod
    def send_message(self, channel_id: int, post: Post, **kwargs) -> DiscordMessage | TelegramMessage:
        pass

    @abstractmethod
    def prepare_kwargs(self, **kwargs) -> dict:
        pass


class DiscordSender(AbstractSender):
    def __init__(self, bot: Bot) -> None:
        self.bot = DiscordBot(bot.token)  # TODO: Add to model Bot field webhook

    def delete_message(self, channel_id: int, message_id: int, **kwargs) -> dict:
        try:
            self.bot.delete_message(channel_id, message_id)
            status = True
        except (RequestException, ValueError) as e:
            logger.exception(e)
            status = False

        return {
            'channel_id': channel_id,
            'message_id': message_id,
            'deleted': status,
        }

    def edit_message(self, channel_id: int, message_id: int, post: Post, **kwargs) -> DiscordMessage:
        return self.bot.edit_message(channel_id, message_id, content=post.message, **kwargs)

    def send_message(self, channel_id: int, post: Post, **kwargs) -> DiscordMessage:
        message = escape_discord_message(post.message)
        return self.bot.send_message(channel_id, message, **kwargs)

    def prepare_kwargs(self, **kwargs) -> dict:
        disable_notification = kwargs.pop('parse_mode', None)
        disable_notification = kwargs.pop('disable_notification', False)

        kwargs.update({
            'silent': disable_notification
        })

        return kwargs


class TelegramSender(AbstractSender):
    def __init__(self, bot: Bot) -> None:
        self.bot = TelegramBot(bot.token)

        self.root = getenv('PROJECT_LOCATION', '')
        if not self.root:
            raise Exception('PROJECT_LOCATION not set in system environment')

    def _get_path(self, filename: str) -> str:
        filename = str(filename)[1:] if str(filename).startswith('/') else path.join('media', str(filename))
        return path.join(self.root, filename)

    def _send_audio(self, channel_id: int, audio: str, *args, **kwargs) -> TelegramMessage:
        with open(self._get_path(audio), mode='rb') as file:
            return self.bot.send_audio(channel_id, file, *args, **kwargs)

    def _send_document(self, channel_id: int, document: str, *args, **kwargs) -> TelegramMessage:
        with open(self._get_path(document), mode='rb') as file:
            return self.bot.send_document(channel_id, file, *args, **kwargs)

    def _send_media_group(self, channel_id, files: List[GalleryDocument | GalleryPhoto], *args, **kwargs) -> List[TelegramMessage]:  # NOQA: E501
        return self.bot.send_media_group(channel_id, files, *args, **kwargs)

    def _send_gallery_documents(self, channel_id: int, documents: QuerySet[GalleryDocument], *args, **kwargs) -> List[TelegramMessage]:  # NOQA: E501
        files = []
        for document in documents:
            with open(self._get_path(document.file), mode='rb') as file:
                files.append(
                    InputMediaDocument(
                        BytesIO(file.read()),
                        caption=escape_telegram_message(document.caption),
                        parse_mode='MarkdownV2',
                    )
                )
        return self._send_media_group(channel_id, files, *args, **kwargs)

    def _send_gallery_photos(self, channel_id: int, photos: QuerySet[GalleryPhoto], *args, **kwargs) -> List[TelegramMessage]:  # NOQA: E501
        files = []
        for photo in photos:
            with open(self._get_path(photo.file), mode='rb') as file:
                files.append(
                    InputMediaPhoto(
                        BytesIO(file.read()),
                        caption=escape_telegram_message(photo.caption),
                        parse_mode='MarkdownV2',
                    )
                )
        return self._send_media_group(channel_id, files, *args, **kwargs)

    def _send_message(self, channel_id: int, message: str, *args, **kwargs) -> TelegramMessage:
        return self.bot.send_message(channel_id, message, *args, **kwargs)

    def _send_photo(self, channel_id: int, photo: str, *args, **kwargs) -> TelegramMessage:
        with open(self._get_path(photo), mode='rb') as file:
            return self.bot.send_photo(channel_id, file, *args, **kwargs)

    def _send_video(self, channel_id: int, video: str, *args, **kwargs) -> TelegramMessage:
        with open(self._get_path(video), mode='rb') as file:
            return self.bot.send_video_note(channel_id, data=file)

    def _send_voice(self, channel_id: int, voice: str, *args, **kwargs) -> TelegramMessage:
        with open(self._get_path(voice), mode='rb') as file:
            return self.bot.send_voice(channel_id, file, *args, **kwargs)

    def delete_message(self, channel_id: int, message_id: int) -> dict:
        try:
            status = self.bot.delete_message(channel_id, message_id)
        except ApiTelegramException:
            status = False
        except Exception as e:
            logger.exception(e)
            status = False

        return {
            'channel_id': channel_id,
            'message_id': message_id,
            'deleted': status,
        }

    def edit_message(self, channel_id: int, message_id: int, post: Post, **kwargs) -> List[TelegramMessage]:
        message = escape_telegram_message(post.message or post.caption)

        if post.message:
            return self.bot.edit_message_text(channel_id, message_id, text=message, **kwargs)

        return self.bot.edit_message_caption(channel_id, message_id, caption=message, **kwargs)

    def send_message(self, channel_id: int, post: Post, **kwargs) -> List[TelegramMessage] | TelegramMessage:
        message = escape_telegram_message(post.message or post.caption)

        if post.audio:
            return self._send_audio(channel_id, post.audio, caption=message, **kwargs)
        elif post.document:
            return self._send_document(channel_id, post.document, caption=message, **kwargs)
        elif post.gallery_documents:
            kwargs.pop('parse_mode', None)  # TODO:
            return self._send_gallery_documents(channel_id, post.gallery_documents.all(), **kwargs)
        elif post.gallery_photos:
            kwargs.pop('parse_mode', None)  # TODO:
            return self._send_gallery_photos(channel_id, post.gallery_photos.all(), **kwargs)
        elif post.message:
            return self._send_message(channel_id, message, **kwargs)
        elif post.photo:
            return self._send_photo(channel_id, post.photo, caption=message, **kwargs)
        elif post.video:
            return self._send_video(channel_id, post.video, caption=message, **kwargs)
        elif post.voice:
            return self._send_voice(channel_id, post.voice, caption=message, **kwargs)
        raise UnknownPostType(f'Unknown post type given from post with id {post.pk}')

    def prepare_kwargs(self, **kwargs) -> dict:
        return kwargs


class Sender:
    senders = {
        MessengerEnum.DISCORD: DiscordSender,
        MessengerEnum.TELEGRAM: TelegramSender,
    }

    def __init__(self, channel: Channel) -> None:
        sender = self.senders.get(channel.channel_type)  # type: ignore

        if not sender:
            raise SenderNotFound(f'Not found sender for channel with type {channel.channel_type}')

        self.sender = sender(channel.bot)

    def delete_message(self, channel_id: int, message_id: int, **kwargs) -> dict:
        return self.sender.delete_message(channel_id, message_id, **kwargs)

    def edit_message(self, channel_id: int, message_id: int, post: Post, **kwargs) -> Any:
        return self.sender.edit_message(channel_id, message_id, post, **kwargs)

    def send_message(self, channel_id: int, post: Post, **kwargs) -> Any:
        return self.sender.send_message(channel_id, post, **kwargs)

    def prepare_kwargs(self, **kwargs) -> dict:
        return self.sender.prepare_kwargs(**kwargs)
