from django.core.handlers.wsgi import WSGIRequest
from django.db.models.signals import pre_delete
from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .exceptions import BotNotSetException
from .models import Bot
from .models import Channel
from .models import Post
from .sender import Sender
from .signals import publish_post_signal
from .signals import unpublish_post_signal
from .signals import edit_post_signal
from .tasks import delete_message_task
from .tasks import delete_post_task
from .tasks import edit_post_task
from .tasks import send_post_task
from .utils import download_bot_photo

import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Bot)
def bot_post_save(sender: Bot, instance: Bot, created: bool, **kwargs) -> None:
    if not created:
        return

    try:
        sender_api = Sender(instance)
        info = sender_api.get_me()
    except Exception as e:
        logger.exception(e)
        info = None

    if info:
        instance.username = info.username
        instance.save()


@receiver(post_save, sender=Channel)
def channel_post_save(sender: Channel, instance: Channel, created: bool, **kwargs) -> None:
    if instance.is_completed:
        return

    if not instance.channel_id:
        return

    if not instance.bot:
        raise BotNotSetException(f'Bot not set from channel with id {instance.pk}')

    sender_api = Sender(instance.bot)
    info = sender_api.get_channel_info(instance.channel_id)

    if info:
        instance.title = info.title
        instance.description = info.description
        instance.is_completed = True

        if sender_api.is_telegram_sender:
            instance.username = info.username
            if info.photo:
                download_bot_photo(instance, info.photo.small_file_id)
        else:
            instance.server_id = info.guild_id
    instance.save()


@receiver(pre_delete, sender=Post)
def post_model_pre_delete(sender: Post, instance: Post, **kwargs) -> None:
    for message in instance.messages.all():
        delete_message_task.delay(message.pk)


@receiver(publish_post_signal)
def publish_post_signal_handler(sender: WSGIRequest, instance: Post, **kwargs) -> None:
    if not instance.channels.all():
        return
    send_post_task.delay(instance.pk, disable_notification=instance.is_silent)


@receiver(m2m_changed, sender=Post.channels.through)
def related_models_changed(sender, instance, action, **kwargs):
    if action == 'post_add':
        send_post_task.delay(instance.pk, disable_notification=instance.is_silent)


@receiver(unpublish_post_signal)
def unpublish_post_signal_handler(sender: WSGIRequest, instance: Post, **kwargs) -> None:
    delete_post_task.delay(instance.pk)


@receiver(edit_post_signal)
def edit_post_signal_handler(sender: WSGIRequest, instance: Post, **kwargs) -> None:
    edit_post_task.delay(instance.pk)
