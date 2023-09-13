from re import search

from discord import SyncWebhook
from discord.types.webhook import Webhook
from requests import Session


class DiscordBot:
    def __init__(self, webhook: str) -> None:
        data = search(r'discord(?:app)?\.com/api/webhooks/(?P<id>[0-9]{17,20})/(?P<token>[A-Za-z0-9\.\-\_]{60,})', webhook) # NOQA
        if data is None:
            raise ValueError('Invalid webhook URL given.')

        self.webhook_id = data['id']
        self.webhook_token = data['token']

    def client(self, chat_id: int) -> SyncWebhook:
        data: Webhook = {
            'id': self.webhook_id,
            'token': self.webhook_token,
            'type': 1,
            'channel_id': chat_id,
        }
        return SyncWebhook(data, session=Session())

    def send_message(self, chat_id: int, message: str, *args, **kwargs) -> None:
        self.client(chat_id).send(message)
