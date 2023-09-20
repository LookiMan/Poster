from json import dumps

from django.db.models.fields.files import ImageFieldFile
from django.db.models import FileField

from requests import Session

from .exceptions import ApiDiscordException
from .types import Channel
from .types import Message
from .types import User


class DiscordBot:

    def __init__(self, token: str) -> None:
        self.token = token

        if not self.token:
            raise Exception('Token must be not empty')

        self.session = Session()

    def _api(self, path: str, method: str = 'GET', **kwargs) -> dict:
        path = path if path.startswith('/') else '/' + path
        headers = {
            'Authorization': f'Bot {self.token}',
        }

        ext_headers = kwargs.pop('headers', None)
        if ext_headers:
            headers.update(ext_headers)

        response = self.session.request(
            method,
            f'https://discord.com/api/v10{path}',
            headers=headers,
            **kwargs,
        )

        if response.status_code not in range(200, 300):
            raise ApiDiscordException(response.text)

        if response.status_code != 204:
            return response.json()
        return {}

    def _send_message(
            self,
            channel_id: int,
            message: str | None = None,
            **kwargs) -> Message:
        multipart = {}
        payload = {}
        flags = 0

        if message:
            payload.update({'content': str(message)})

        attachments = kwargs.pop('attachments', False)
        if attachments:
            payload.update({'attachments': attachments})  # type: ignore

        disable_notification = kwargs.pop('disable_notification', False)
        if disable_notification:
            flags = 1 << 12  # 4096

        voice_message = kwargs.pop('voice_message', False)
        if voice_message:
            flags += 1 << 13  # 8192

        if flags:
            payload.update({'flags': flags})  # type: ignore

        embeds = kwargs.pop('embeds', False)
        if embeds:
            payload.update({'embeds': embeds})  # type: ignore

        file = kwargs.pop('file', None)
        files = [file] if file else kwargs.pop('files', None)

        if files:
            if embeds:
                multipart.update({'payload_json': (None, dumps(payload), 'application/json')})
                payload = None

                for index, file in enumerate(files):
                    multipart.update({f'files[{index}]': file})
            else:
                multipart = files

        return Message(self._api(f'/channels/{channel_id}/messages', 'POST', data=payload, files=multipart))

    def get_me(self) -> User:
        return User(self._api('/users/@me'))

    def get_channel_info(self, channel_id: int) -> Channel:
        return Channel(self._api(f'/channels/{channel_id}'))

    def is_channel_with_id_exists(self, channel_id: int) -> bool:
        try:
            return self.get_channel_info(channel_id) is not None
        except ApiDiscordException:
            return False

    def delete_message(self, channel_id: int, message_id: int) -> None:
        self._api(f'/channels/{channel_id}/messages/{message_id}', 'DELETE')

    def edit_message(self, channel_id: int, message_id: int, message, **kwargs) -> Message:
        json = {
            'content': message,
        }
        return Message(self._api(f'/channels/{channel_id}/messages/{message_id}', 'PATCH', json=json))

    def send_audio(self, channel_id: int, audio: FileField, caption: str, **kwargs) -> Message:
        return self._send_message(channel_id, message=caption, file=(audio.name, audio), **kwargs)

    def send_document(self, channel_id: int, document: FileField, caption: str, **kwargs) -> Message:
        return self._send_message(channel_id, message=caption, file=(document.name, document), **kwargs)

    def send_photo(self, channel_id: int, photo: ImageFieldFile, caption: str, **kwargs) -> Message:
        return self._send_message(channel_id, message=caption, file=(photo.name, photo), **kwargs)

    def send_message(self, channel_id: int, message: str, **kwargs) -> Message:
        return self._send_message(channel_id, message, **kwargs)

    def send_media_group(self, channel_id: int, files: list, attachments: list, embeds: list, **kwargs):
        return self._send_message(channel_id, files=files, embeds=embeds, attachments=attachments, **kwargs)

    def send_voice(self, channel_id: int, voice: FileField, *args, **kwargs) -> Message:
        return self._send_message(channel_id, file=(voice.name, voice), voice_message=True, **kwargs)
