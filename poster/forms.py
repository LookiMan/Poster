from magic import Magic

from django.forms import CharField
from django.forms import Textarea
from django.forms import ModelForm
from django.forms import ValidationError
from django.utils.translation import gettext_lazy as _

from froala_editor.widgets import FroalaEditor

from telebot.apihelper import ApiTelegramException

from .enums import PostTypeEnum
from .models import Bot
from .models import Channel
from .models import GalleryDocument
from .models import GalleryPhoto
from .models import Post

from telegram import TelegramBot


class BotAdminForm(ModelForm):

    class Meta:
        model = Bot
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()
        try:
            TelegramBot(cleaned_data.get('token')).get_me()
        except ApiTelegramException:
            raise ValidationError(
                _('Unable to retrieve bot telegram data for this token')
            )


class ChannelAdminForm(ModelForm):

    class Meta:
        model = Channel
        fields = '__all__'

    def clean(self):
        cleaned_data = super().clean()

        channel_id = cleaned_data.get('channel_id')
        if channel_id and (not channel_id < 0 or len(str(channel_id)) < 12):
            raise ValidationError(
                _('Not valid Channel ID given. For example: -100000000000')
            )

        bot = cleaned_data.get('bot')
        if bot and channel_id and not TelegramBot(bot.token).is_channel_with_id_exists(channel_id):
            raise ValidationError(
                _(
                    'Check the correctness of the specified Channel ID or '
                    'make sure that the bot is added to the channel with administrator rights'
                )
            )


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
            if not audio:
                raise ValidationError(_('Audio file required'))

            elif not mime.from_buffer(audio.read()).startswith('audio/'):
                raise ValidationError(_('Select audio file'))
            audio.seek(0)

        elif self.instance.post_type == PostTypeEnum.DOCUMENT and not cleaned_data.get('document'):
            raise ValidationError(_('Document file required'))

        elif self.instance.post_type == PostTypeEnum.TEXT and not cleaned_data.get('message'):
            raise ValidationError(_('Text message required'))

        elif self.instance.post_type == PostTypeEnum.PHOTO and not cleaned_data.get('photo'):
            raise ValidationError(_('Photo file required'))

        elif self.instance.post_type == PostTypeEnum.VIDEO:
            video = cleaned_data.get('video')
            if not video:
                raise ValidationError(_('Video file required'))

            elif not mime.from_buffer(video.read()).startswith('video/'):
                raise ValidationError(_('Select video file'))
            video.seek(0)

        elif self.instance.post_type == PostTypeEnum.VOICE:
            voice = cleaned_data.get('voice')
            if not voice:
                raise ValidationError(_('Voice file required'))

            elif not mime.from_buffer(voice.read()).startswith('audio/'):
                raise ValidationError(_('Select audio file'))
            voice.seek(0)


class GalleryDocumentInlineForm(ModelForm):
    class Meta:
        model = GalleryDocument
        fields = '__all__'

    caption = CharField(
        widget=Textarea(attrs={'rows': 1, 'cols': 80}),
        label=_('Document caption'),
        help_text=_('Description that will be displayed under this file'),
    )


class GalleryPhotoInlineForm(ModelForm):
    class Meta:
        model = GalleryPhoto
        fields = '__all__'

    caption = CharField(
        widget=Textarea(attrs={'class': 'form-control', 'rows': 1, 'cols': 80}),
        label=_('Photo caption'),
        help_text=_('Description that will be displayed under this photo'),
    )
