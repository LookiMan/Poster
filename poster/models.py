from django.db.models import BooleanField
from django.db.models import BigIntegerField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import FileField
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.db.models import ImageField
from django.db.models import TextField
from django.db.models import UUIDField
from django.db.models import SET_NULL
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from froala_editor.fields import FroalaField

from .enums import PostChannelEnum
from .enums import PostTypeEnum
from .enums import TaskTypeEnum
from .mixins import BaseMixin
from .mixins import ChannelsMixin
from .mixins import ImageMixin


class Bot(BaseMixin, ImageMixin):
    bot_id = BigIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Bot id'),
    )

    token = CharField(
        max_length=255,
        verbose_name=_('Telegram bot token'),
        help_text=_(
            'Create a Telegram bot using @BotFather and copy the received token into this field.<br>'
            'Token example: 0123456789:XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX'
        ),
    )

    first_name = CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_('Telegram bot first name'),
    )

    last_name = CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_('Telegram bot last name'),
    )

    username = CharField(
        null=True,
        blank=True,
        max_length=255,
        verbose_name=_('Telegram bot username'),
    )

    can_join_groups = BooleanField(
        default=False,
        verbose_name=_('Can join to groups'),
    )

    def __str__(self):
        return f'@{self.username}'

    class Meta:
        ordering = ['-created_at']

        verbose_name = _('Bot')
        verbose_name_plural = _('Bots')


class Channel(BaseMixin, ImageMixin):
    bot = ForeignKey(
        'Bot',
        null=True,
        on_delete=SET_NULL,
        verbose_name=_('Bot'),
        help_text=_('Select the previously created Telegram bot that you added to the Telegram channel as an administrator'), # NOQA
    )

    channel_id = BigIntegerField(
        verbose_name=_('Channel id'),
        help_text=_('Insert your channel id'),
    )

    channel_type = CharField(
        max_length=255,
        choices=PostChannelEnum.choices,
        default=PostChannelEnum.TELEGRAM,
        verbose_name=_('Channel type'),
        help_text=_('Available: {}'.format('; '.join([str(l) for l in PostChannelEnum.labels]))),
    )

    title = CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Channel name'),
        help_text=_('Name retrieved automatically via API'),
    )

    description = CharField(
        null=True,
        blank=True,
        verbose_name=_('Channel description'),
        help_text=_('Description retrieved automatically via API'),
    )

    username = CharField(
        null=True,
        blank=True,
        verbose_name=_('Channel username'),
        help_text=_('Username retrieved automatically via API'),
    )

    invite_link = CharField(
        null=True,
        blank=True,
        verbose_name=_('Channel link'),
        help_text=_('Link retrieved automatically via API'),
    )

    def __str__(self):
        return f'{self.get_channel_type_display()} channel: {self.title}'

    class Meta:
        ordering = ['-created_at']

        verbose_name = _('Channel')
        verbose_name_plural = _('Channels')


class GalleryDocument(BaseMixin):
    post = ForeignKey(
        'Post',
        null=True,
        blank=True,
        on_delete=CASCADE,
    )

    file = FileField(_('Document'))

    caption = TextField(
        blank=True,
        null=True,
        verbose_name=_('document caption'),
        help_text=_('Insert document caption'),
    )

    class Meta:
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')


class GalleryPhoto(BaseMixin):
    post = ForeignKey(
        'Post',
        null=True,
        blank=True,
        on_delete=CASCADE,
    )

    file = ImageField(_('Photo'))

    caption = TextField(
        blank=True,
        null=True,
        verbose_name=_('photo caption'),
        help_text=_('Insert photo caption'),
    )

    class Meta:
        verbose_name = _('Photo')
        verbose_name_plural = _('Photos')


class Post(BaseMixin, ChannelsMixin):
    post_type = CharField(
        max_length=32,
        choices=PostTypeEnum.choices,
        verbose_name=_('Post type'),
        help_text=_('Select post type to continue'),
    )

    audio = FileField(
        blank=True,
        null=True,
        verbose_name=_('Audio file'),
        help_text=_('Select an audio file to send as a voice message'),
    )

    document = FileField(
        blank=True,
        null=True,
        verbose_name=_('Document file'),
        help_text=_(''),
    )

    video = FileField(
        blank=True,
        null=True,
        verbose_name=_('Video file'),
        help_text=_(''),
    )

    photo = ImageField(
        blank=True,
        null=True,
        verbose_name=_('Photo file'),
        help_text=_(''),
    )

    voice = FileField(
        blank=True,
        null=True,
        verbose_name=_('Voice file'),
        help_text=_(''),
    )

    caption = FroalaField(
        blank=True,
        null=True,
        verbose_name=_('Caption'),
        help_text=_('Insert caption (max length 255 symbols)'),
    )

    message = FroalaField(
        blank=True,
        null=True,
        verbose_name=_('Message text'),
        help_text=_('Enter the text to send it to the channel. The maximum length for one message is 4096 characters'), # NOQA
    )

    is_published = BooleanField(
        default=False,
        verbose_name=_('Is published')
    )

    messages = ManyToManyField(
        'PostMessage',
        verbose_name=_('Messages'),
        related_name='messages',
    )

    @property
    def gallery_documents(self):
        return GalleryDocument.objects.filter(post_id=self.id)

    @property
    def gallery_photos(self):
        return GalleryPhoto.objects.filter(post_id=self.id)

    @property
    def is_media_gallery(self):
        return self.post_type in [PostTypeEnum.GALLERY_DOCUMENTS, PostTypeEnum.GALLERY_PHOTOS]

    def __str__(self):
        return f'{self.post_type} post with id {self.id}'

    class Meta:
        ordering = ['-updated_at']

        verbose_name = _('Post')
        verbose_name_plural = _('Posts')


class PostMessage(BaseMixin):
    channel = ForeignKey(
        'Channel',
        null=True,
        on_delete=SET_NULL,
        verbose_name=_('Channel'),
    )

    message_id = BigIntegerField(
        verbose_name=_('Message id'),
    )

    def __str__(self):
        return f'Channel message id: {self.message_id}'


class Task(BaseMixin):

    created_at = DateTimeField(
        verbose_name=_('Date of creation'),
        auto_now_add=True,
        null=True,
    )

    task_id = UUIDField(
        verbose_name=_('Celery task id'),
    )

    channel = ForeignKey(
        'Channel',
        on_delete=SET_NULL,
        null=True,
        verbose_name=_('Channel'),
    )

    task_type = CharField(
        null=True,
        max_length=32,
        choices=TaskTypeEnum.choices,
        verbose_name=_('Task type'),
        help_text=_('Type of action at which the record was created'),
    )

    response = TextField(
        null=True,
        verbose_name=_('Response data'),
        help_text=_('Automatically recorded result of sending a message'),
    )

    exception = TextField(
        null=True,
        verbose_name=_('Exception data'),
        help_text=_('Automatically detected exception to sending a message'),
    )

    post = ForeignKey(
        'Post',
        on_delete=SET_NULL,
        null=True,
        verbose_name=_('Post'),
        help_text=_('Original post'),
    )

    def __str__(self):
        return f'{self.channel and self.channel.title}'

    class Meta:
        ordering = ['-created_at']

        verbose_name = _('Task')
        verbose_name_plural = _('Tasks')
