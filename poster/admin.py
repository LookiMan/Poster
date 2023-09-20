from django.contrib.admin import register
from django.contrib.admin import ModelAdmin
from django.contrib.admin import TabularInline
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from .forms import BotAdminForm
from .forms import ChannelAdminForm
from .forms import GalleryDocumentInlineForm
from .forms import GalleryPhotoInlineForm
from .forms import PostAdminForm
from .enums import PostTypeEnum
from .enums import TaskTypeEnum
from .mixins import AdminImageMixin
from .models import Bot
from .models import Channel
from .models import GalleryDocument
from .models import GalleryPhoto
from .models import Post
from .models import Task
from .signals import edit_post_signal
from .signals import publish_post_signal
from .signals import unpublish_post_signal


class GalleryDocumentInline(TabularInline):
    model = GalleryDocument
    extra = 1
    form = GalleryDocumentInlineForm


class GalleryPhotoInline(TabularInline):
    model = GalleryPhoto
    extra = 1
    form = GalleryPhotoInlineForm


@register(Bot)
class BotAdmin(ModelAdmin):
    model = Bot
    form = BotAdminForm

    list_display = (
        'username',
        'bot_type',
        'token_preview',
    )

    def get_user_fields(self, request, obj=None):
        return ['bot_type', 'token']

    def get_auto_fields(self, request, obj=None):
        if not obj:
            return []
        return ['username']

    def get_fieldsets(self, request, obj=None):
        return [
            (None, {'fields': [
                *self.get_user_fields(request, obj),
                *self.get_auto_fields(request, obj),
            ]})
        ]

    def get_readonly_fields(self, request, obj=None):
        readonly_files = ['username']

        if obj:
            readonly_files.extend(['bot_type', 'token'])

        return (*self.readonly_fields, *readonly_files)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def token_preview(self, obj):
        if not obj.token:
            return 'Token: -'
        return f'Token: {"*" * len(obj.token[:-4])}{obj.token[-4:]}'


@register(Channel)
class ChannelAdmin(AdminImageMixin, ModelAdmin):
    model = Channel
    form = ChannelAdminForm

    list_display = (
        'title',
        'channel_type',
        'username',
        'description',
        'is_completed',
    )

    def get_user_fields(self, request, obj=None):
        fields = ['channel_type']
        if obj:
            fields.extend(['channel_id', 'bot'])

            if obj.is_completed and obj.server_id:
                fields.append('server_id')

        return fields

    def get_auto_fields(self, request, obj=None):
        fields = []

        if not obj:
            return fields

        if obj and obj.is_completed:
            fields.extend([
                'title',
                'username',
                'description',
            ])

        return fields

    def get_fieldsets(self, request, obj=None):
        return [
            (None, {'fields': [
                *self.get_user_fields(request, obj),
                *self.get_auto_fields(request, obj),
            ]})
        ]

    def get_readonly_fields(self, request, obj=None):
        readonly_files = [
            'title',
            'username',
            'description',
        ]

        if obj:
            if obj.channel_type:
                readonly_files.append('channel_type')

            if obj.is_completed:
                readonly_files.extend(['bot', 'channel_id', 'server_id'])

        return (*self.readonly_fields, *readonly_files)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        model = self.get_object(request, object_id)
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = not model.is_completed
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.channel_type and form and form.base_fields.get('bot'):
            form.base_fields['bot'].queryset = Bot.objects.filter(bot_type=obj.channel_type)
        return form


@register(Post)
class PostAdmin(ModelAdmin):
    model = Post
    form = PostAdminForm

    list_display = (
        'post_type',
        'is_published',
        'post_content',
        'post_channels',
        'created_at',
        'updated_at',
    )

    def get_content_fields(self, request, obj=None):
        fields = {
            PostTypeEnum.AUDIO: ['audio', 'caption'],
            PostTypeEnum.DOCUMENT: ['document', 'caption'],
            PostTypeEnum.TEXT: ['message'],
            PostTypeEnum.PHOTO: ['photo', 'caption'],
            PostTypeEnum.VIDEO: ['video', 'caption'],
            PostTypeEnum.VOICE: ['voice', 'caption'],
        }
        return fields.get(obj and obj.post_type, [])

    def get_after_content_fields(self, request, obj=None):
        fields = []

        if obj and obj.is_published:
            fields.append('messages_links')

        return fields

    def get_before_content_fields(self, request, obj=None):
        if not obj:
            return ['post_type']
        return [
            'channels',
            'is_published',
            'created_at',
            'updated_at',
        ]

    def get_fieldsets(self, request, obj=None):
        return [
            (None, {'fields': [
                *self.get_before_content_fields(request, obj),
                *self.get_content_fields(request, obj),
                *self.get_after_content_fields(request, obj),
            ]})
        ]

    def get_inlines(self, request, obj=None):
        if obj and obj.post_type == PostTypeEnum.GALLERY_DOCUMENTS:
            return (*self.inlines, GalleryDocumentInline)
        elif obj and obj.post_type == PostTypeEnum.GALLERY_PHOTOS:
            return (*self.inlines, GalleryPhotoInline)
        return self.inlines

    def get_readonly_fields(self, request, obj=None):
        readonly_files = [
            'is_published',
            'created_at',
            'updated_at',
            'messages_links',
        ]

        if obj and obj.is_published:
            readonly_files.extend([
                'post_type',
                'channels',
                'audio',
                'document',
                'photo',
                'video',
                'voice',
            ])

        return (*self.readonly_fields, *readonly_files)

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_publish'] = False
        extra_context['show_save_and_unpublish'] = False
        extra_context['show_save_and_add_another'] = False
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        model = self.get_object(request, object_id)
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_publish'] = not model.is_published
        extra_context['show_save_and_unpublish'] = model.is_published
        extra_context['show_save_and_edit'] = model.is_published
        extra_context['disable_save_and_edit_button'] = model.is_media_gallery
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if form.data.get('_save_and_publish'):
            obj.is_published = True
            obj.is_silent = False
            publish_post_signal.send(sender=request, instance=obj)
        elif form.data.get('_save_and_publish_silently'):
            obj.is_published = True
            obj.is_silent = True
            publish_post_signal.send(sender=request, instance=obj)
        elif form.data.get('_save_and_unpublish'):
            obj.is_published = False
            unpublish_post_signal.send(sender=request, instance=obj)
        elif form.data.get('_save_and_edit'):
            edit_post_signal.send(sender=request, instance=obj)
        super().save_model(request, obj, form, change)

    def messages_links(self, obj):
        template = '''
        <a class="list-group-item list-group-item-action" href="{href}">
            View message in channel {channel}
        </a>
        '''

        return mark_safe('<ul class="list-group">{}</ul>'.format(
            ''.join([
                template.format(href=message.href, channel=message.channel_name)
                for message in obj.messages.all() if message.channel and message.message_id
            ])
        ))

    messages_links.allow_tags = True
    messages_links.short_description = _('Messages links')

    def post_content(self, obj):
        if obj.post_type == PostTypeEnum.AUDIO:
            return mark_safe(
                f'<strong>{_("Audio")}:</strong> {obj.audio}.<br><strong>{_("Caption")}:</strong> {obj.caption}'
            )
        elif obj.post_type == PostTypeEnum.DOCUMENT:
            return mark_safe(
                f'<strong>{_("Document")}:</strong> {obj.document}.<br><strong>{_("Caption")}:</strong> {obj.caption}' # NOQA
            )
        elif obj.post_type == PostTypeEnum.TEXT:
            return mark_safe(
                f'<strong>{_("Message")}:</strong> {obj.message}'
            )
        elif obj.post_type == PostTypeEnum.PHOTO:
            return mark_safe(
                f'<strong>{_("Photo")}:</strong> {obj.photo}.<br><strong>{_("Caption")}:</strong> {obj.caption}'
            )
        elif obj.post_type == PostTypeEnum.VIDEO:
            return mark_safe(
                f'<strong>{_("Video")}:</strong> {obj.video}.<br><strong>{_("Caption")}:</strong> {obj.caption}'
            )
        elif obj.post_type == PostTypeEnum.VOICE:
            return mark_safe(
                f'<strong>{_("Voice")}:</strong> {obj.voice}.<br><strong>{_("Caption")}:</strong> {obj.caption}'
            )

    post_content.allow_tags = True
    post_content.short_description = _('Post content')

    def post_channels(self, obj):
        return mark_safe('<br>'.join([str(channel) for channel in obj.channels.all()]))

    post_channels.allow_tags = True
    post_channels.short_description = _('Post channels')

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if form and form.base_fields.get('channels'):
            form.base_fields['channels'].queryset = Channel.objects.filter(is_completed=True)
        return form


@register(Task)
class TaskAdmin(ModelAdmin):
    model = Task

    list_display = (
        'task_id',
        'action_type',
        'action_status',
        'channel',
        'created_at',
    )

    def action_status(self, obj):
        return mark_safe(
            f'<strong class="text-{"success" if obj.response else "danger"}">{_("SUCCESS") if obj.response else _("FAIL")}</strong>' # NOQA
        )

    def action_type(self, obj):
        color = {
            TaskTypeEnum.CREATE: 'text-green',
            TaskTypeEnum.UPDATE: 'text-info',
            TaskTypeEnum.DELETE: 'text-warning',
        }
        return mark_safe(
            f'<strong class="{color.get(obj.task_type, "text-danger")}">{obj.get_task_type_display() or _("UNKNOWN")}</strong>' # NOQA
        )

    action_status.short_description = _('Action status')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
