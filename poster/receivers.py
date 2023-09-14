from django.core.handlers.wsgi import WSGIRequest
from django.db.models.signals import pre_delete
from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .enums import MessengerEnum
from .exceptions import BotNotSetException
from .models import Bot
from .models import Channel
from .models import Post
from .signals import publish_post_signal
from .signals import unpublish_post_signal
from .signals import edit_post_signal
from .tasks import delete_message_task
from .tasks import delete_post_task
from .tasks import edit_post_task
from .tasks import send_post_task
from .utils import save_file

from telegram_bot import TelegramBot

import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Bot)
def bot_post_save(sender: Bot, instance: Bot, created: bool, **kwargs) -> None:
    if not created:
        return

    if instance.bot_type == MessengerEnum.DISCORD:
        return

    elif instance.bot_type == MessengerEnum.TELEGRAM:
        try:
            info = TelegramBot(instance.token).get_me()
        except Exception as e:
            logger.exception(e)
            info = None

        if info:
            instance.username = info.username
            instance.save()
    else:
        logger.error(f'Created bot with unknown type {instance.bot_type}')


@receiver(post_save, sender=Channel)
def channel_post_save(sender: Channel, instance: Channel, created: bool, **kwargs) -> None:
    if not created:
        return

    if not instance.is_completed:
        return

    if not instance.bot:
        raise BotNotSetException(f'Bot not set from channel with id {instance.pk}')

    bot = TelegramBot(instance.bot.token)
    info = bot.get_channel_info(instance.channel_id)

    if info:
        instance.title = info.title
        instance.description = info.description
        instance.username = info.username
        instance.invite_link = info.invite_link

        if info.photo:
            file_id = info.photo.small_file_id
            content = bot.download_file_from_telegram(file_id)
            if content:
                instance.image.name = file_id
                save_file(file_id, content)

    instance.save()


@receiver(pre_delete, sender=Post)
def post_model_pre_delete(sender: Post, instance: Post, **kwargs) -> None:
    for message in instance.messages.all():
        delete_message_task.delay(message.pk)


@receiver(publish_post_signal)
def publish_post_signal_handler(sender: WSGIRequest, instance: Post, **kwargs) -> None:
    disable_notification = kwargs.get('disable_notification', False)

    if instance.channels.all():
        send_post_task.delay(instance.pk, disable_notification=disable_notification)
    else:
        @receiver(m2m_changed, sender=Post.channels.through, dispatch_uid='0001')
        def related_models_changed(sender, instance, action, **kwargs):
            if action == 'post_add':
                send_post_task.delay(instance.pk, disable_notification=disable_notification)


@receiver(unpublish_post_signal)
def unpublish_post_signal_handler(sender: WSGIRequest, instance: Post, **kwargs) -> None:
    delete_post_task.delay(instance.pk)


@receiver(edit_post_signal)
def edit_post_signal_handler(sender: WSGIRequest, instance: Post, **kwargs) -> None:
    edit_post_task.delay(instance.pk)
