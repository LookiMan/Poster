from .enums import RecordTypeEnum
from .models import Channel
from .models import Post
from .models import PostMessage
from .models import Record
from .sender import Sender
from config.celery import app

from telegram import TelegramBot

import logging
logger = logging.getLogger(__name__)


@app.task(name='poster.tasks.publish_post', bind=True)
def publish_post(self, channel_pk: int, post_pk: int, *, disable_notification: bool) -> None:
    channel = Channel.objects.filter(pk=channel_pk).first()
    post = Post.objects.filter(pk=post_pk).first()

    if not channel:
        logger.exception(f'Channel with id {channel_pk} not found')
    if channel and not channel.bot:
        logger.exception(f'Bot not found from Channel with id {channel_pk}')
    if not post:
        logger.exception(f'Post with id {post_pk} not found')

    if not (channel and post and channel.bot):
        return

    record = Record(
        record_type=RecordTypeEnum.CREATE,
        channel_id=channel.pk,
        task_id=self.request.id,
        post_id=post.pk,
    )

    try:
        sender = Sender(TelegramBot(channel.bot.token))
        response = sender.send_post(
            channel,
            post,
            disable_notification=disable_notification,
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        logger.exception(e)
        record.exception = e
    else:
        record.response = response
        response_messages = response if isinstance(response, list) else [response]
        for response_message in response_messages:
            message = PostMessage(
                channel_id=channel.pk,
                channel_username=channel.username,
                message_id=response_message.message_id,
            )
            message.save()

            post = Post.objects.get(pk=post.pk)
            if post:
                post.messages.add(message)

    record.save()


@app.task(name='poster.tasks.unpublish_post', bind=True)
def unpublish_post(self, channel_pk: int, post_pk: int) -> None:
    channel = Channel.objects.filter(pk=channel_pk).first()
    post = Post.objects.filter(pk=post_pk).first()

    if not channel:
        logger.exception(f'Channel with id {channel_pk} not found')
    if channel and not channel.bot:
        logger.exception(f'Bot not found from Channel with id {channel_pk}')
    if not post:
        logger.exception(f'Post with id {post_pk} not found')

    if not (channel and post and channel.bot):
        return

    for message in post.messages.all():
        record = Record(
            record_type=RecordTypeEnum.DELETE,
            channel_id=channel.pk,
            task_id=self.request.id,
        )

        try:
            sender = Sender(TelegramBot(channel.bot.token))
            record.response = sender.delete_post(channel.channel_id, message.message_id)
        except Exception as e:
            logger.exception(e)
            record.exception = e
        message.delete()

        record.save()


@app.task(name='poster.tasks.edit_post', bind=True)
def edit_post(self, channel_pk: int, post_pk: int) -> None:
    channel = Channel.objects.filter(pk=channel_pk).first()
    post = Post.objects.filter(pk=post_pk).first()

    if not channel:
        logger.exception(f'Channel with id {channel_pk} not found')
    if channel and not channel.bot:
        logger.exception(f'Bot not found from Channel with id {channel_pk}')
    if not post:
        logger.exception(f'Post with id {post_pk} not found')

    if not (channel and post and channel.bot):
        return

    record = Record(
        record_type=RecordTypeEnum.UPDATE,
        channel_id=channel.pk,
        task_id=self.request.id,
    )

    try:
        sender = Sender(TelegramBot(channel.bot.token))
        record.response = sender.edit_post(
            channel,
            post,
            parse_mode='MarkdownV2'
        )
    except Exception as e:
        logger.exception(e)
        record.exception = e

    record.save()


@app.task(name='poster.tasks.delete_telegram_message', bind=True)
def delete_telegram_message(self, channel_pk: int, message_pk: int) -> None:
    channel = Channel.objects.filter(pk=channel_pk).first()
    message = PostMessage.objects.filter(pk=message_pk).first()

    if not channel:
        logger.exception(f'Channel with id {channel_pk} not found')
    if channel and not channel.bot:
        logger.exception(f'Bot not found from Channel with id {channel_pk}')
    if not message:
        logger.exception(f'Message with pk {message_pk} not found')

    if not (channel and message and channel.bot):
        return

    record = Record(
        record_type=RecordTypeEnum.DELETE,
        channel_id=channel.pk,
        task_id=self.request.id,
    )

    try:
        sender = Sender(TelegramBot(channel.bot.token))
        record.response = sender.delete_post(channel.channel_id, message.message_id)
    except Exception as e:
        logger.exception(e)
        record.exception = e
    message.delete()
    record.save()
