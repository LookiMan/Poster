from django.db.models import BooleanField
from django.db.models import BigIntegerField
from django.db.models import CharField
from django.db.models import DateTimeField
from django.db.models import FileField
from django.db.models import ForeignKey
from django.db.models import ManyToManyField
from django.db.models import ImageField
from django.db.models import IntegerField
from django.db.models import TextField
from django.db.models import UUIDField
from django.db.models import SET_NULL
from django.db.models import CASCADE
from django.utils.translation import gettext_lazy as _

from froala_editor.fields import FroalaField

from .enums import PostTypeEnum
from .enums import RecordTypeEnum
from .mixins import BaseMixin
from .mixins import ChannelsMixin


class Bot(BaseMixin):
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


class Channel(BaseMixin):
    bot = ForeignKey(
        'Bot',
        null=True,
        on_delete=SET_NULL,
        verbose_name=_('Telegram bot'),
        help_text=_('Select the previously created Telegram bot that you added to the Telegram channel as an administrator'), # NOQA
    )

    channel_id = BigIntegerField(
        verbose_name=_('Telegram channel id'),
        help_text=_(''),
    )

    title = CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Telegram channel name'),
        help_text=_(''),
    )

    description = CharField(
        null=True,
        blank=True,
        verbose_name=_('Telegram channel description'),
        help_text=_(''),
    )

    username = CharField(
        null=True,
        blank=True,
        verbose_name=_('Telegram channel username'),
        help_text=_(''),
    )

    invite_link = CharField(
        null=True,
        blank=True,
        verbose_name=_('Telegram channel invite link'),
        help_text=_(''),
    )

    image = ImageField(
        null=True,
        blank=True,
        verbose_name=_('Channel image'),
    )

    def __str__(self):
        return f'Telegram channel: {self.title}'

    class Meta:
        ordering = ['-pk']

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

    def __str__(self):
        return f'{self.post_type} post with id {self.id}'

    class Meta:
        ordering = ['-created_at']

        verbose_name = _('Post')
        verbose_name_plural = _('Posts')


class PostMessage(BaseMixin):
    channel_id = IntegerField(
        verbose_name=_('Channel id'),
    )

    channel_username = CharField(
        max_length=255,
        verbose_name=_('Channel username'),
    )

    message_id = BigIntegerField(
        verbose_name=_('Message id'),
    )

    def __str__(self):
        return f'Channel message id: {self.message_id}'


class Record(BaseMixin):

    created_at = DateTimeField(
        verbose_name=_('Date of creation'),
        auto_now_add=True,
        null=True,
    )

    task_id = UUIDField(
        unique=False,
        verbose_name=_('Celery task id'),
    )

    channel = ForeignKey(
        'Channel',
        on_delete=SET_NULL,
        null=True,
        verbose_name=_('Channel'),
    )

    record_type = CharField(
        null=True,
        max_length=32,
        choices=RecordTypeEnum.choices,
        verbose_name=_('Record type'),
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

        verbose_name = _('Record')
        verbose_name_plural = _('Records')
