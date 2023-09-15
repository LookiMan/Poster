from django.db.models import BooleanField
from django.db.models import BigIntegerField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import FileField
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.db.models import ImageField
from django.db.models import QuerySet
from django.db.models import TextField
from django.db.models import UUIDField
from django.db.models import SET_NULL
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from froala_editor.fields import FroalaField

from .enums import MessengerEnum
from .enums import PostTypeEnum
from .enums import TaskTypeEnum
from .mixins import BaseMixin
from .mixins import ChannelsMixin
from .mixins import ImageMixin


class Bot(BaseMixin):
    bot_type: CharField = CharField(
        max_length=255,
        choices=MessengerEnum.choices,
        default=MessengerEnum.TELEGRAM,
        verbose_name=_('Bot type'),
        help_text=_('Available types: {}').format('; '.join([str(label) for label in MessengerEnum.labels])),
    )

    token: CharField = CharField(
        max_length=255,
        verbose_name=_('Bot token'),
        help_text=_(
            'Create a Telegram bot using @BotFather and copy the received token into this field.<br>'
            'Token example: 0123456789:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX<br><br>'
            'Create a Discord bot using Developers > Applications > New Application.<br>'
            'Token example: XXXXXXXXXXXXXXXXXXXXXXXXXX.XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        ),
    )

    username: CharField = CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_('Bot username'),
    )

    def __str__(self) -> str:
        return self.username or str(_('Bot username not set'))

    class Meta:
        ordering = ['-created_at']

        verbose_name = _('Bot')
        verbose_name_plural = _('Bots')


class Channel(BaseMixin, ImageMixin):
    bot: ForeignKey = ForeignKey(
        'Bot',
        null=True,
        on_delete=SET_NULL,
        verbose_name=_('Bot'),
        help_text=_('Previously created bot'),
    )

    channel_type: CharField = CharField(
        max_length=255,
        choices=MessengerEnum.choices,
        verbose_name=_('Channel type'),
        help_text=_('Available types: {}').format('; '.join([str(label) for label in MessengerEnum.labels])),
    )

    channel_id: BigIntegerField = BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Channel id'),
        help_text=_('Insert your channel id'),
    )

    server_id: BigIntegerField = BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Discord server id'),
        help_text=_('Insert your discord server id'),
    )

    title: CharField = CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Channel title'),
        help_text=_('Name retrieved automatically via API'),
    )

    description: TextField = TextField(
        null=True,
        blank=True,
        verbose_name=_('Channel description'),
        help_text=_('Description retrieved automatically via API'),
    )

    username: CharField = CharField(
        null=True,
        blank=True,
        verbose_name=_('Channel username'),
        help_text=_('Username retrieved automatically via API'),
    )

    is_completed: BooleanField = BooleanField(
        default=False,
        verbose_name=_('Is completed')
    )

    def __str__(self) -> str:
        return f'{self.get_channel_type_display()} channel: {self.title}'  # type: ignore

    class Meta:
        ordering = ['-created_at']

        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')


class GalleryDocument(BaseMixin):
    post: ForeignKey = ForeignKey(
        'Post',
        null=True,
        blank=True,
        on_delete=CASCADE,
        verbose_name=_('Post'),
    )

    file: FileField = FileField(_('Document'))

    caption: TextField = TextField(
        blank=True,
        null=True,
        verbose_name=_('Document caption'),
        help_text=_('Insert document caption'),
    )

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')


class GalleryPhoto(BaseMixin):
    post: ForeignKey = ForeignKey(
        'Post',
        null=True,
        blank=True,
        on_delete=CASCADE,
        verbose_name=_('Post'),
    )

    file: ImageField = ImageField(_('Photo'))

    caption: TextField = TextField(
        blank=True,
        null=True,
        verbose_name=_('Photo caption'),
        help_text=_('Insert photo caption'),
    )

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')


class Post(BaseMixin, ChannelsMixin):
    post_type: CharField = CharField(
        max_length=32,
        choices=PostTypeEnum.choices,
        verbose_name=_('Post type'),
        help_text=_('Select post type to continue'),
    )

    audio: FileField = FileField(
        blank=True,
        null=True,
        verbose_name=_('Audio file'),
        help_text=_('Select an audio file to send as a voice message'),
    )

    document: FileField = FileField(
        blank=True,
        null=True,
        verbose_name=_('Document file'),
        help_text=_('Select a document file to send'),
    )

    video: FileField = FileField(
        blank=True,
        null=True,
        verbose_name=_('Video file'),
        help_text=_('Select a video file to send'),
    )

    photo: ImageField = ImageField(
        blank=True,
        null=True,
        verbose_name=_('Photo file'),
        help_text=_('Select a photo file to send'),
    )

    voice: FileField = FileField(
        blank=True,
        null=True,
        verbose_name=_('Voice file'),
        help_text=_('Select a audio file to send'),
    )

    caption: FroalaField = FroalaField(
        blank=True,
        null=True,
        verbose_name=_('Caption'),
        help_text=_('Insert caption (max length 255 symbols)'),
    )

    message: FroalaField = FroalaField(
        blank=True,
        null=True,
        verbose_name=_('Message text'),
        help_text=_('Enter the text to send it to the channel. The maximum length for one message is 4096 characters'), # NOQA
    )

    is_published: BooleanField = BooleanField(
        default=False,
        verbose_name=_('Is published')
    )

    messages: ManyToManyField = ManyToManyField(
        'PostMessage',
        verbose_name=_('Messages'),
        related_name='messages',
    )

    @property
    def gallery_documents(self) -> QuerySet:
        return GalleryDocument.objects.filter(post_id=self.pk)

    @property
    def gallery_photos(self) -> QuerySet:
        return GalleryPhoto.objects.filter(post_id=self.pk)

    @property
    def is_media_gallery(self) -> bool:
        return self.post_type in [PostTypeEnum.GALLERY_DOCUMENTS, PostTypeEnum.GALLERY_PHOTOS]

    def __str__(self) -> str:
        return f'{self.post_type} post with id {self.pk}'

    class Meta:
        ordering = ['-updated_at']

        verbose_name = _('Post')
        verbose_name_plural = _('Posts')


class PostMessage(BaseMixin):
    channel: ForeignKey = ForeignKey(
        'Channel',
        null=True,
        on_delete=SET_NULL,
        verbose_name=_('Channel'),
    )

    message_id: BigIntegerField = BigIntegerField(
        verbose_name=_('Message id'),
    )

    @property
    def href(self) -> str:
        channel = self.channel
        if not channel:
            return '#'
        elif channel.channel_type == MessengerEnum.DISCORD:
            return f'https://discord.com/channels/{channel.server_id}/{channel.channel_id}/{self.message_id}'
        elif channel.channel_type == MessengerEnum.TELEGRAM:
            return f'https://t.me/{channel.username}/{self.message_id}'
        else:
            return '#'

    def __str__(self) -> str:
        return f'Channel message id: {self.message_id}'


class Task(BaseMixin):

    created_at: DateTimeField = DateTimeField(
        verbose_name=_('Date of creation'),
        auto_now_add=True,
        null=True,
    )

    task_id: UUIDField = UUIDField(
        verbose_name=_('Celery task id'),
    )

    channel: ForeignKey = ForeignKey(
        'Channel',
        on_delete=SET_NULL,
        null=True,
        verbose_name=_('Channel'),
    )

    task_type: CharField = CharField(
        null=True,
        max_length=32,
        choices=TaskTypeEnum.choices,
        verbose_name=_('Task type'),
        help_text=_('Type of action at which the record was created'),
    )

    response: TextField = TextField(
        null=True,
        verbose_name=_('Response data'),
        help_text=_('Automatically recorded result of sending a message'),
    )

    exception: TextField = TextField(
        null=True,
        verbose_name=_('Exception data'),
        help_text=_('Automatically detected exception to sending a message'),
    )

    post: ForeignKey = ForeignKey(
        'Post',
        on_delete=SET_NULL,
        null=True,
        verbose_name=_('Post'),
        help_text=_('Original post'),
    )

    def __str__(self) -> str:
        return f'{self.channel and self.channel.title}'

    class Meta:
        ordering = ['-created_at']

        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
