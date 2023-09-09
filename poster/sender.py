from typing import List
from io import BytesIO
from os import path
from os import getenv

from django.db.models import QuerySet

from telebot.types import Message
from telebot.types import InputMediaDocument
from telebot.types import InputMediaPhoto

from .exceptions import UnknownPostType
from .models import Channel
from .models import GalleryDocument
from .models import GalleryPhoto
from .models import Post
from .utils import prepare_message

from telegram import TelegramBot


class Sender:
    def __init__(self, bot: TelegramBot) -> None:
        self.bot = bot

        self.root = getenv('PROJECT_LOCATION', '')
        if not self.root:
            raise Exception('PROJECT_LOCATION not set in system environment')

    def _get_path(self, filename: str) -> str:
        filename = str(filename)[1:] if str(filename).startswith('/') else path.join('media', str(filename))
        return path.join(self.root, filename)

    def _send_audio(self, channel_id: int, audio: str, *args, **kwargs) -> Message:
        with open(self._get_path(audio), mode='rb') as file:
            return self.bot.send_audio(channel_id, file, *args, **kwargs)

    def _send_document(self, channel_id: int, document: str, *args, **kwargs) -> Message:
        with open(self._get_path(document), mode='rb') as file:
            return self.bot.send_document(channel_id, file, *args, **kwargs)

    def _send_media_group(self, channel_id, files: List[GalleryDocument | GalleryPhoto], *args, **kwargs) -> List[Message]: # NOQA
        return self.bot.send_media_group(channel_id, files, *args, **kwargs)

    def _send_gallery_documents(self, channel_id: int, documents: QuerySet[GalleryDocument], *args, **kwargs) -> List[Message]: # NOQA
        files = []
        for document in documents:
            with open(self._get_path(document.file), mode='rb') as file:
                files.append(
                    InputMediaDocument(
                        BytesIO(file.read()),
                        caption=prepare_message(document.caption),
                        parse_mode='MarkdownV2',
                    )
                )
        return self._send_media_group(channel_id, files, *args, **kwargs)

    def _send_gallery_photos(self, channel_id: int, photos: QuerySet[GalleryPhoto], *args, **kwargs) -> List[Message]: # NOQA
        files = []
        for photo in photos:
            with open(self._get_path(photo.file), mode='rb') as file:
                files.append(
                    InputMediaPhoto(
                        BytesIO(file.read()),
                        caption=prepare_message(photo.caption),
                        parse_mode='MarkdownV2',
                    )
                )
        return self._send_media_group(channel_id, files, *args, **kwargs)

    def _send_message(self, channel_id: int, message: str, *args, **kwargs) -> Message:
        return self.bot.send_message(channel_id, message, *args, **kwargs)

    def _send_photo(self, channel_id: int, photo: str, *args, **kwargs) -> Message:
        with open(self._get_path(photo), mode='rb') as file:
            return self.bot.send_photo(channel_id, file, *args, **kwargs)

    def _send_video(self, channel_id: int, video: str, *args, **kwargs) -> Message:
        with open(self._get_path(video), mode='rb') as file:
            return self.bot.send_video_note(channel_id, data=file)

    def _send_voice(self, channel_id: int, voice: str, *args, **kwargs) -> Message:
        with open(self._get_path(voice), mode='rb') as file:
            return self.bot.send_voice(channel_id, file, *args, **kwargs)

    def delete_post(self, channel_id: int, message_id: int) -> bool:
        return self.bot.delete_message(channel_id, message_id)

    def edit_post(self, channel: Channel, post: Post, **kwargs) -> List[Message]:
        responses = []
        for message in post.messages.all():
            if post.message:
                responses.append(
                    self.bot.edit_message_text(
                        channel.channel_id,
                        message.message_id,
                        text=prepare_message(post.message),
                        **kwargs,
                    )
                )
            else:
                responses.append(
                    self.bot.edit_message_caption(
                        channel.channel_id,
                        message.message_id,
                        caption=prepare_message(post.caption),
                        **kwargs,
                    )
                )
        return responses

    def send_post(self, channel: Channel, post: Post, **kwargs) -> List[Message] | Message:
        if post.audio:
            return self._send_audio(
                channel.channel_id,
                post.audio,
                caption=prepare_message(post.caption),
                **kwargs
            )
        elif post.document:
            return self._send_document(
                channel.channel_id,
                post.document,
                caption=prepare_message(post.caption),
                **kwargs
            )
        elif post.gallery_documents:
            kwargs.pop('parse_mode', None)  # TODO:
            return self._send_gallery_documents(
                channel.channel_id,
                post.gallery_documents.all(),
                **kwargs
            )
        elif post.gallery_photos:
            kwargs.pop('parse_mode', None)  # TODO:
            return self._send_gallery_photos(
                channel.channel_id,
                post.gallery_photos.all(),
                **kwargs
            )
        elif post.message:
            return self._send_message(
                channel.channel_id,
                prepare_message(post.message),
                **kwargs
            )
        elif post.photo:
            return self._send_photo(
                channel.channel_id,
                post.photo,
                caption=prepare_message(post.caption),
                **kwargs
            )
        elif post.video:
            return self._send_video(
                channel.channel_id,
                post.video,
                caption=prepare_message(post.caption),
                **kwargs
            )
        elif post.voice:
            return self._send_voice(
                channel.channel_id,
                post.voice,
                caption=prepare_message(post.caption),
                **kwargs
            )
        raise UnknownPostType(f'Unknown post type given from post with id {post.pk}')
