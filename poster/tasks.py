from telebot.types import Message as TelegramMessage

from .enums import TaskTypeEnum
from .models import Post
from .models import PostMessage
from .sender import Sender
from .models import Task
from config.celery import app

import logging
logger = logging.getLogger(__name__)


def delete_message(self, message: PostMessage) -> None:
    task = Task(
        task_type=TaskTypeEnum.DELETE,
        channel_id=message.channel.pk,
        task_id=self.request.id,
    )

    try:
        sender = Sender(message.channel)
        task.response = sender.delete_message(message.channel.channel_id, message.message_id)
    except Exception as e:
        logger.exception(e)
        task.exception = e

    task.save()


@app.task(name='poster.tasks.delete_post_task', bind=True)
def delete_post_task(self, post_pk: int) -> None:
    post = Post.objects.filter(pk=post_pk).first()
    if not post:
        logger.exception(f'Post with id {post_pk} not found')
        return

    for message in post.messages.all():
        delete_message(self, message)


@app.task(name='poster.tasks.delete_message_task', bind=True)
def delete_message_task(self, message_pk: int) -> None:
    message = PostMessage.objects.filter(pk=message_pk).first()
    if not message:
        logger.exception(f'Message with id {message_pk} not found')
        return

    delete_message(self, message)


@app.task(name='poster.tasks.edit_post_task', bind=True)
def edit_post_task(self, post_pk: int) -> None:
    post = Post.objects.filter(pk=post_pk).first()
    if not post:
        logger.exception(f'Post with id {post_pk} not found')
        return

    for message in post.messages.all():
        task = Task(
            task_type=TaskTypeEnum.UPDATE,
            channel_id=message.channel.pk,
            task_id=self.request.id,
        )

        try:
            sender = Sender(message.channel)
            task.response = sender.edit_message(
                message.channel.channel_id,
                message.message_id,
                post,
                parse_mode='MarkdownV2'
            )
        except Exception as e:
            logger.exception(e)
            task.exception = e

        task.save()


@app.task(name='poster.tasks.send_post_task', bind=True)
def send_post_task(self, post_pk: int, *, disable_notification: bool) -> None:
    post = Post.objects.filter(pk=post_pk).first()
    if not post:
        logger.exception(f'Post with id {post_pk} not found')
        return

    for channel in post.channels.all():
        task = Task(
            task_type=TaskTypeEnum.CREATE,
            channel_id=channel.pk,
            task_id=self.request.id,
            post_id=post.pk,
        )

        try:
            sender = Sender(channel)
            kwargs = sender.prepare_kwargs(
                disable_notification=disable_notification,
                parse_mode='MarkdownV2',
            )
            response = sender.send_message(channel.channel_id, post, **kwargs)
        except Exception as e:
            logger.exception(e)
            task.exception = e
        else:
            task.response = response
            response = response if isinstance(response, list) else [response]

            for message in response:
                message = PostMessage(
                    channel_id=channel.pk,
                    message_id=message.message_id if isinstance(message, TelegramMessage) else message.id,
                )
                message.save()
                post.messages.add(message)

        task.save()
