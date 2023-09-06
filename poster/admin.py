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
from .enums import RecordTypeEnum
from .models import Bot
from .models import Channel
from .models import GalleryDocument
from .models import GalleryPhoto
from .models import Post
from .models import Record


class GalleryDocumentInline(TabularInline):
    model = GalleryDocument
    extra = 1
    form = GalleryDocumentInlineForm
    fields = (
        'file',
        'caption',
    )

    def clean(self):
        super().clean()

        for form in self.forms:
            data = form.cleaned_data
            raise Exception(data)


class GalleryPhotoInline(TabularInline):
    model = GalleryPhoto
    extra = 1
    form = GalleryPhotoInlineForm
    fields = (
        'file',
        'caption',
    )


@register(Bot)
class BotAdmin(ModelAdmin):
    model = Bot
    form = BotAdminForm

    list_display = (
        'bot_id',
        'first_name',
        'last_name',
        'username',
        'can_join_groups',
    )

    def get_fields(self, request, obj=None):
        if not obj:
            self.exclude = self.list_display
        return super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (*self.readonly_fields, *self.list_display, 'token')
        return self.readonly_fields

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


@register(Channel)
class ChannelAdmin(ModelAdmin):
    model = Channel
    form = ChannelAdminForm

    list_display = (
        'title',
        'username',
        'description',
        'invite_link',
        'preview_image',
    )

    def get_fields(self, request, obj=None):
        if not obj:
            self.exclude = ('image', *self.list_display)
        else:
            self.exclude = ('image',)
        return super().get_fields(request, obj)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (*self.readonly_fields, *self.list_display, 'channel_id')
        return self.readonly_fields

    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="75">')
        else:
            return _('[Image not set]')

    preview_image.short_description = _('Channel image')

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        return super().change_view(request, object_id, form_url, extra_context=extra_context)


@register(Post)
class PostAdmin(ModelAdmin):
    model = Post
    form = PostAdminForm

    dynamic_fields = (
        'audio',
        'caption',
        'channels',
        'document',
        'message',
        'photo',
        'video',
        'voice',
    )

    service_fields = (
        'messages',
        'is_published',
    )

    list_display = (
        'post_type',
        'is_published',
        'post_content',
        'created_at',
    )

    readonly_fields = ()

    def get_fields(self, request, obj=None):
        all_fields = ['audio', 'document', 'caption', 'message', 'photo', 'video', 'voice']
        exclude_fields = {
            PostTypeEnum.AUDIO: set(all_fields).difference(set(['audio', 'caption'])),
            PostTypeEnum.DOCUMENT: set(all_fields).difference(set(['document', 'caption'])),
            PostTypeEnum.GALLERY_DOCUMENTS: all_fields,
            PostTypeEnum.GALLERY_PHOTOS: all_fields,
            PostTypeEnum.TEXT: set(all_fields).difference(set(['message'])),
            PostTypeEnum.PHOTO: set(all_fields).difference(set(['photo', 'caption'])),
            PostTypeEnum.VIDEO: set(all_fields).difference(set(['video', 'caption'])),
            PostTypeEnum.VOICE: set(all_fields).difference(set(['voice', 'caption'])),
        }

        if not obj:
            self.exclude = (*self.dynamic_fields, *self.service_fields)
        else:
            self.exclude = (*exclude_fields.get(obj.post_type, []), *self.service_fields)
        return super().get_fields(request, obj)

    def get_inlines(self, request, obj=None):
        if obj and obj.post_type == PostTypeEnum.GALLERY_DOCUMENTS:
            return (*self.inlines, GalleryDocumentInline)
        elif obj and obj.post_type == PostTypeEnum.GALLERY_PHOTOS:
            return (*self.inlines, GalleryPhotoInline)
        return self.inlines

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return (*self.readonly_fields, 'post_type', 'is_published', 'messages_links')
        return self.readonly_fields

    def add_view(self, request, form_url='', extra_context=None):
        extra_context = extra_context or {}
        extra_context['show_save'] = False
        extra_context['show_save_and_publish'] = False
        extra_context['show_save_and_unpublish'] = False
        extra_context['show_save_and_add_another'] = False
        return super().add_view(request, form_url, extra_context=extra_context)

    def change_view(self, request, object_id, form_url='', extra_context=None):
        extra_context = extra_context or {}
        model = self.get_object(request, object_id)
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False
        extra_context['show_save_and_continue'] = False
        extra_context['show_save_and_publish'] = not model.is_published
        extra_context['show_save_and_unpublish'] = model.is_published
        extra_context['show_save_and_edit'] = model.is_published
        return super().change_view(request, object_id, form_url, extra_context=extra_context)

    def save_model(self, request, obj, form, change):
        if form.data.get('_save_and_publish'):
            obj.is_published = True
        elif form.data.get('_save_and_unpublish'):
            obj.is_published = False
        super().save_model(request, obj, form, change)

    def messages_links(self, obj):
        template = '''
        <a class="list-group-item list-group-item-action" href="https://t.me/{channel_username}/{message_id}">
            View message in channel @{channel_username}
        </a>
        '''

        return mark_safe('<ul class="list-group">{}</ul>'.format(
            ''.join([
                template.format(channel_username=message.channel_username, message_id=message.message_id)
                for message in obj.messages.all()
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


@register(Record)
class RecordAdmin(ModelAdmin):
    model = Record

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
            RecordTypeEnum.CREATE: 'text-green',
            RecordTypeEnum.UPDATE: 'text-info',
            RecordTypeEnum.DELETE: 'text-warning',
        }
        return mark_safe(
            f'<strong class="{color.get(obj.record_type, "text-danger")}">{obj.get_record_type_display() or _("UNKNOWN")}</strong>' # NOQA
        )

    action_status.short_description = _('Action status')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser
