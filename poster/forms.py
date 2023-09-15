from json import dumps
from magic import Magic

from django.conf import settings
from django.forms import CharField
from django.forms import HiddenInput
from django.forms import ModelForm
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from froala_editor.widgets import FroalaEditor
from munch import munchify
from telebot.apihelper import ApiTelegramException

from .enums import MessengerEnum
from .enums import PostTypeEnum
from .mixins import MediaGalleryMixin
from .models import Bot
from .models import Channel
from .models import GalleryDocument
from .models import GalleryPhoto
from .models import Post

from discord_bot import ApiDiscordException
from discord_bot import DiscordBot
from telegram_bot import TelegramBot

import logging
logger = logging.getLogger(__name__)


class InlineFroalaEditor(FroalaEditor):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.options.update({
            'toolbarInline': True,
            'charCounterCount': False,
        })


class BotAdminForm(ModelForm):
    messages = munchify({
        'discord_token_error': _('Unable to retrieve bot telegram data for this token'),
        'telegram_token_error': _('Unable to retrieve bot discord data for this token'),
        'unknown_bot_type': _('Unknown bot type specified')
    })

    class Meta:
        model = Bot
        fields = '__all__'

    def _validate_discord_token(self, token: str) -> None:
        try:
            DiscordBot(token).get_me()
        except ApiDiscordException:
            raise ValidationError(self.messages.discord_token_error)

    def _validate_telegram_token(self, token: str) -> None:
        try:
            TelegramBot(token).get_me()
        except ApiTelegramException:
            raise ValidationError(self.messages.telegram_token_error)

    def clean(self):
        cleaned_data = super().clean()
        if not self.is_valid():
            return

        bot_type = cleaned_data.get('bot_type')
        token = cleaned_data.get('token')

        if bot_type == MessengerEnum.DISCORD:
            self._validate_discord_token(token)
        elif bot_type == MessengerEnum.TELEGRAM:
            self._validate_telegram_token(token)
        else:
            raise ValidationError(self.messages.unknown_bot_type)


class ChannelAdminForm(ModelForm):
    messages = munchify({
        'channel_id_required': _('Channel id field is required'),
        'channel_id_error': _(
            'Check the correctness of the specified Channel ID or '
            'make sure that the bot is added to the channel with administrator rights'
        ),
    })

    class Meta:
        model = Channel
        fields = '__all__'

    def _validate_discord_fields(self) -> None:
        if not DiscordBot(self.bot.token).is_channel_with_id_exists(self.channel_id):
            raise ValidationError(self.messages.channel_id_error)

    def _validate_telegram_fields(self) -> None:
        if not TelegramBot(self.bot.token).is_channel_with_id_exists(self.channel_id):
            raise ValidationError(self.messages.channel_id_error)

    def clean(self):
        cleaned_data = super().clean()
        self.bot = cleaned_data.get('bot')
        self.channel_id = cleaned_data.get('channel_id')

        if self.bot:
            if not self.channel_id:
                raise ValidationError(self.messages.channel_id_required)
            elif self.bot.bot_type == MessengerEnum.DISCORD:
                self._validate_discord_fields()
            elif self.bot.bot_type == MessengerEnum.TELEGRAM:
                self._validate_telegram_fields()


class PostAdminForm(ModelForm):

    class Meta:
        model = Post
        fields = '__all__'

        widgets = {
            'caption': FroalaEditor(),
            'message': FroalaEditor(),
        }

    def clean(self):
        cleaned_data = super().clean()
        mime = Magic(mime=True)

        if self.instance.post_type == PostTypeEnum.AUDIO:
            audio = cleaned_data.get('audio')
            if not (self.instance.audio or audio):
                raise ValidationError(_('Audio file required'))

            if audio:
                if not mime.from_buffer(audio.read()).startswith('audio/'):
                    raise ValidationError(_('Select audio file'))
                audio.seek(0)

        elif self.instance.post_type == PostTypeEnum.DOCUMENT:
            if not (self.instance.document or cleaned_data.get('document')):
                raise ValidationError(_('Document file required'))

        elif self.instance.post_type == PostTypeEnum.TEXT and not cleaned_data.get('message'):
            raise ValidationError(_('Text message required'))

        elif self.instance.post_type == PostTypeEnum.PHOTO:
            if not (self.instance.photo or cleaned_data.get('photo')):
                raise ValidationError(_('Photo file required'))

        elif self.instance.post_type == PostTypeEnum.VIDEO:
            video = cleaned_data.get('video')
            if not (self.instance.video or video):
                raise ValidationError(_('Video file required'))

            if video:
                if not mime.from_buffer(video.read()).startswith('video/'):
                    raise ValidationError(_('Select video file'))
                video.seek(0)

        elif self.instance.post_type == PostTypeEnum.VOICE:
            voice = cleaned_data.get('voice')
            if not (self.instance.voice or voice):
                raise ValidationError(_('Voice file required'))

            if voice:
                if not mime.from_buffer(voice.read()).startswith('audio/'):
                    raise ValidationError(_('Select audio file'))
                voice.seek(0)


class BaseGalleryInlineForm(ModelForm, MediaGalleryMixin):
    froala_editor_options = CharField(widget=HiddenInput, initial=dumps(settings.FROALA_EDITOR_OPTIONS))


class GalleryDocumentInlineForm(BaseGalleryInlineForm):

    class Meta:
        model = GalleryDocument
        fields = '__all__'

    caption = CharField(
        widget=InlineFroalaEditor(attrs={'rows': 1, 'cols': 80}),
        label=_('Document caption'),
        help_text=_('Description that will be displayed under this file'),
    )


class GalleryPhotoInlineForm(BaseGalleryInlineForm):

    class Meta:
        model = GalleryPhoto
        fields = '__all__'

    caption = CharField(
        widget=InlineFroalaEditor(attrs={'class': 'form-control', 'rows': 1, 'cols': 80}),
        label=_('Photo caption'),
        help_text=_('Description that will be displayed under this photo'),
    )
