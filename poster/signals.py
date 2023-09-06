from django.db.models.signals import pre_delete
from django.db.models.signals import pre_save
from django.db.models.signals import post_save
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from .models import Bot
from .models import Channel
from .models import Post
from .tasks import delete_telegram_message
from .tasks import edit_post
from .tasks import publish_post
from .tasks import unpublish_post
from .utils import save_file

from telegram import TelegramBot

import logging
logger = logging.getLogger(__name__)


@receiver(post_save, sender=Bot)
def bot_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    try:
        info = TelegramBot(instance.token).get_me()
    except Exception as e:
        logger.exception(e)
        info = None

    if info:
        instance.bot_id = info.id
        instance.first_name = info.first_name
        instance.last_name = info.last_name
        instance.username = info.username
        instance.can_join_groups = info.can_join_groups
        instance.save()


@receiver(post_save, sender=Channel)
def channel_post_save(sender, instance, created, **kwargs):
    if not created:
        return

    bot = TelegramBot(instance.bot.token)
    info = bot.get_channel_info(instance.channel_id)

    if info:
        instance.title = info.title
        instance.description = info.description
        instance.username = info.username
        instance.invite_link = info.invite_link

        if info.photo:
            file_id = info.photo.small_file_id

            instance.image.name = file_id
            save_file(file_id, bot.download_file_from_telegram(file_id))

    instance.save()


@receiver(pre_save, sender=Post)
def post_model_pre_save(sender, instance, **kwargs):
    model = Post.objects.filter(pk=instance.pk).first()
    if not model:
        return

    channels = instance.channels.all()
    if channels:
        for channel in channels:
            if model.message != instance.message or model.caption != instance.caption:
                edit_post.delay(channel.id, instance.id)
    else:
        @receiver(m2m_changed, sender=Post.channels.through, dispatch_uid='0001')
        def related_models_changed(sender, instance, action, **kwargs):
            if action == 'post_add':
                for channel in channels:
                    if model.message != instance.message or model.caption != instance.caption:
                        edit_post.delay(channel.id, instance.id)


@receiver(post_save, sender=Post)
def post_model_post_save(sender, instance, created, **kwargs):
    channels = instance.channels.all()
    if channels:
        if instance.is_published:
            for channel in channels:
                publish_post.delay(channel.id, instance.id)
        else:
            for channel in channels:
                unpublish_post.delay(channel.id, instance.id)

    else:
        @receiver(m2m_changed, sender=Post.channels.through, dispatch_uid='0002')
        def related_models_changed(sender, instance, action, **kwargs):
            if action == 'post_add':
                for channel in instance.channels.all():
                    if instance.is_published:
                        publish_post.delay(channel.id, instance.id)
                    else:
                        unpublish_post.delay(channel.id, instance.id)


@receiver(pre_delete, sender=Post)
def post_model_pre_delete(sender, instance, **kwargs):
    for message in instance.messages.all():
        delete_telegram_message.delay(message.channel_id, message.id)
