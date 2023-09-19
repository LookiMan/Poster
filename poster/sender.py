from abc import abstractmethod
from abc import ABC
from typing import List
from io import BytesIO
from os import path
from os import getenv

from django.db.models import QuerySet
from telebot.apihelper import ApiTelegramException
from telebot.types import Chat as TelegramChat
from telebot.types import Message as TelegramMessage
from telebot.types import User as TelegramUser
from telebot.types import InputMediaDocument
from telebot.types import InputMediaPhoto

from .enums import MessengerEnum
from .exceptions import SenderNotFound
from .exceptions import UnknownPostType
from .models import Bot
from .models import GalleryDocument
from .models import GalleryPhoto
from .models import Post
from .utils import escape_discord_message
from .utils import escape_telegram_message

from discord_bot import DiscordBot
from discord_bot import Channel as DiscordChannel
from discord_bot import Message as DiscordMessage
from discord_bot import User as DiscordUser
from discord_bot.exceptions import ApiDiscordException
from telegram_bot import TelegramBot

import logging
logger = logging.getLogger(__name__)


SenderChannel = TelegramChat | DiscordChannel
SenderMessage = TelegramMessage | DiscordMessage
SenderUser = TelegramUser | DiscordUser


class AbstractSender(ABC):
    def __init__(self) -> None:
        self.root = getenv('PROJECT_LOCATION', '')
        if not self.root:
            raise Exception('PROJECT_LOCATION not set in system environment')

    def _get_path(self, filename: str) -> str:
        filename = str(filename)[1:] if str(filename).startswith('/') else path.join('media', str(filename))
        return path.join(self.root, filename)

    @abstractmethod
    def delete_message(self, channel_id: int, message_id: int, **kwargs) -> dict:
        pass

    @abstractmethod
    def edit_message(self, channel_id: int, message_id: int, post: Post, **kwargs) -> TelegramMessage:
        pass

    @abstractmethod
    def send_message(self, channel_id: int, post: Post, **kwargs) -> TelegramMessage:
        pass

    def get_channel_info(self, channel_id: int) -> SenderChannel:
        pass

    def get_me(self) -> SenderUser:
        pass


class DiscordSender(AbstractSender):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = DiscordBot(bot.token)

    # def _send_document(self, channel_id: int, document: str, *args, **kwargs) -> DiscordMessage:
    #     with open(self._get_path(document), mode='rb') as file:
    #         return self.bot.send_document(channel_id, file, *args, **kwargs)

    def _send_gallery_photos(self, channel_id: int, photos: QuerySet[GalleryPhoto], *args, **kwargs) -> DiscordMessage:  # NOQA: E501
        embeds = []
        attachments = []
        files = []
        for index, photo in enumerate(photos):
            with open(self._get_path(photo.file), mode='rb') as file:
                attachments.append({
                    'id': index,
                    'filename': photo.file.name,
                })
                embeds.append({
                    'description': escape_discord_message(photo.caption) if photo.caption else '',
                    'image': {
                        'url': f'attachment://{photo.file.name}',
                    },
                })
                files.append((photo.file.name, BytesIO(file.read())))

        headers = {
            'Content-Disposition': 'form-data; name="payload_json"',
            'Content-Type': 'multipart/form-data',
        }

        return self._send_media_group(
            channel_id,
            files,
            embeds=embeds,
            attachments=attachments,
            headers=headers,
            **kwargs,
        )

    def _send_media_group(self, channel_id, files: List[tuple], **kwargs) -> DiscordMessage:
        return self.bot.send_media_group(channel_id, files, **kwargs)

    def _send_message(self, channel_id: int, post: Post, **kwargs) -> DiscordMessage:
        return self.bot.send_message(channel_id, escape_discord_message(post.message), **kwargs)

    def delete_message(self, channel_id: int, message_id: int, **kwargs) -> dict:
        try:
            self.bot.delete_message(channel_id, message_id)
            status = True
        except ApiDiscordException:
            status = False
        except Exception as e:
            logger.exception(e)
            status = False

        return {
            'channel_id': channel_id,
            'message_id': message_id,
            'deleted': status,
        }

    def edit_message(self, channel_id: int, message_id: int, post: Post, **kwargs):
        message = escape_discord_message(post.message)
        return self.bot.edit_message(channel_id, message_id, message=message, **kwargs)

    def send_message(self, channel_id: int, post: Post, **kwargs):
        if post.gallery_documents:
            pass
        elif post.gallery_photos:
            return self._send_gallery_photos(channel_id, post.gallery_photos.all(), **kwargs)
        else:
            message = escape_discord_message(post.message or post.caption)
            if post.document:
                pass
                # return self.bot.send_document(channel_id, post.document, caption=message, **kwargs)

            elif post.message:
                return self.bot.send_message(channel_id, message, **kwargs)

        raise UnknownPostType(f'Unknown post type given from post with id {post.pk}')

    def get_channel_info(self, channel_id: int) -> DiscordChannel:
        return self.bot.get_channel_info(channel_id)

    def get_me(self) -> DiscordUser:
        return self.bot.get_me()


class TelegramSender(AbstractSender):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = TelegramBot(bot.token)

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
        kwargs.update({'parse_mode': 'MarkdownV2'})
        message = escape_telegram_message(post.message or post.caption)

        if post.message:
            return self.bot.edit_message_text(channel_id, message_id, text=message, **kwargs)

        return self.bot.edit_message_caption(channel_id, message_id, caption=message, **kwargs)

    def send_message(self, channel_id: int, post: Post, **kwargs) -> List[TelegramMessage] | TelegramMessage:
        if post.gallery_documents:
            return self._send_gallery_documents(channel_id, post.gallery_documents.all(), **kwargs)
        elif post.gallery_photos:
            return self._send_gallery_photos(channel_id, post.gallery_photos.all(), **kwargs)
        else:
            kwargs.update({'parse_mode': 'MarkdownV2'})
            message = escape_telegram_message(post.message or post.caption)

            if post.audio:
                return self._send_audio(channel_id, post.audio, caption=message, **kwargs)
            elif post.document:
                return self._send_document(channel_id, post.document, caption=message, **kwargs)
            elif post.message:
                return self._send_message(channel_id, message, **kwargs)
            elif post.photo:
                return self._send_photo(channel_id, post.photo, caption=message, **kwargs)
            elif post.video:
                return self._send_video(channel_id, post.video, caption=message, **kwargs)
            elif post.voice:
                return self._send_voice(channel_id, post.voice, caption=message, **kwargs)

        raise UnknownPostType(f'Unknown post type given from post with id {post.pk}')

    def get_channel_info(self, channel_id: int) -> TelegramChat:
        return self.bot.get_channel_info(channel_id)

    def get_me(self) -> TelegramUser:
        return self.bot.get_me()


class Sender(AbstractSender):
    senders = {
        MessengerEnum.DISCORD: DiscordSender,
        MessengerEnum.TELEGRAM: TelegramSender,
    }

    def __init__(self, bot: Bot) -> None:
        sender = self.senders.get(bot.bot_type)

        if not sender:
            raise SenderNotFound(f'Not found sender for channel with type {bot.bot_type}')

        self.sender = sender(bot)

    @property
    def is_telegram_sender(self):
        return isinstance(self.sender, TelegramSender)

    def delete_message(self, channel_id: int, message_id: int, **kwargs) -> dict:
        return self.sender.delete_message(channel_id, message_id, **kwargs)

    def edit_message(self, channel_id: int, message_id: int, post: Post, **kwargs) -> SenderMessage:
        return self.sender.edit_message(channel_id, message_id, post, **kwargs)

    def send_message(self, channel_id: int, post: Post, **kwargs) -> SenderMessage:
        return self.sender.send_message(channel_id, post, **kwargs)

    def get_channel_info(self, channel_id: int) -> SenderChannel:
        return self.sender.get_channel_info(channel_id)

    def get_me(self) -> SenderUser:
        return self.sender.get_me()
