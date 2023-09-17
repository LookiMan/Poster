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

        response = self.session.request(
            method,
            f'https://discord.com/api/v10{path}',
            headers=headers,
            **kwargs,
        )

        if response.status_code not in range(200, 300):
            raise ApiDiscordException(response.reason)

        if response.status_code != 204:
            return response.json()
        return {}

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

    def send_message(self, channel_id: int, message: str, **kwargs) -> Message:
        json = {
            'content': message
        }

        disable_notification = kwargs.pop('disable_notification', False)
        if disable_notification:
            json.update({'flags': 4096})  # type: ignore

        return Message(self._api(f'/channels/{channel_id}/messages', 'POST', json=json))
