from typing import List
from typing import Optional
from io import BufferedReader

from telebot import TeleBot
from telebot.apihelper import ApiException
from telebot.types import Chat
from telebot.types import Message
from telebot.types import User

from .enums import BotActionTypeEnum

import logging
logger = logging.getLogger(__name__)


class TelegramBot:
    def __init__(self, token: str) -> None:
        self.telebot = TeleBot(token=token)

    def delete_message(self, channel_id: int, message_id) -> bool:
        return self.telebot.delete_message(channel_id, message_id)

    def edit_message_caption(self, channel_id: int, message_id: int, *, caption: str, **kwargs) -> Message:
        return self.telebot.edit_message_caption(chat_id=channel_id, message_id=message_id, caption=caption, **kwargs) # NOQA

    def edit_message_text(self, channel_id: int, message_id: int, *, text: str, **kwargs) -> Message:
        return self.telebot.edit_message_text(chat_id=channel_id, message_id=message_id, text=text, **kwargs)

    def download_file_from_telegram(self, file_id: str) -> Optional[bytes]:
        metadata = self.telebot.get_file(file_id)

        if not metadata:
            return None

        return self.telebot.download_file(metadata.file_path)

    def is_channel_with_id_exists(self, channel_id: int) -> bool:
        try:
            self.telebot.get_chat(channel_id)
        except ApiException:
            return False
        return True

    def get_channel_info(self, channel_id: int) -> Optional[Chat]:
        try:
            channel_info = self.telebot.get_chat(channel_id)
        except ApiException as e:
            channel_info = None
            logger.exception(e)
        return channel_info

    def get_me(self) -> User:
        return self.telebot.get_me()

    def send_audio(self, chat_id: int, audio: BufferedReader, *args, **kwargs) -> Message:
        self.telebot.send_chat_action(chat_id, action=BotActionTypeEnum.UPLOAD_AUDIO)
        return self.telebot.send_audio(chat_id, audio, *args, **kwargs)

    def send_document(self, chat_id: int, document: BufferedReader, *args, **kwargs) -> Message:
        self.telebot.send_chat_action(chat_id, action=BotActionTypeEnum.UPLOAD_DOCUMENT)
        return self.telebot.send_document(chat_id, document, *args, **kwargs)

    def send_photo(self, chat_id: int, photo: BufferedReader, *args, **kwargs) -> Message:
        self.telebot.send_chat_action(chat_id, action=BotActionTypeEnum.UPLOAD_PHOTO)
        return self.telebot.send_photo(chat_id, photo, *args, **kwargs)

    def send_message(self, chat_id: int, message: str, *args, **kwargs) -> Message:
        self.telebot.send_chat_action(chat_id, action=BotActionTypeEnum.TYPING)
        return self.telebot.send_message(chat_id, text=message, *args, **kwargs)

    def send_media_group(self, chat_id: int, files: list, *args, **kwargs) -> List[Message]:
        return self.telebot.send_media_group(chat_id, files, *args, **kwargs)

    def send_video(self, chat_id: int, video_id: str, *args, **kwargs) -> Message:
        self.telebot.send_chat_action(chat_id, action=BotActionTypeEnum.UPLOAD_VIDEO)
        return self.telebot.send_video(chat_id, video_id, *args, **kwargs)

    def send_video_note(self, chat_id: int, data: BufferedReader, *args, **kwargs) -> Message:
        return self.telebot.send_video_note(chat_id, data, *args, **kwargs)

    def send_voice(self, chat_id: int, voice: BufferedReader, *args, **kwargs) -> Message:
        self.telebot.send_chat_action(chat_id, action=BotActionTypeEnum.UPLOAD_VOICE)
        return self.telebot.send_voice(chat_id, voice, *args, **kwargs)
