from django.db.models import DateTimeField
from django.db.models import ImageField
from django.db.models import ManyToManyField
from django.db.models import Model
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from .utils import get_default_telegram_image


class BaseMixin(Model):
    created_at = DateTimeField(
        verbose_name=_('Date of creation'),
        auto_now_add=True,
        null=True,
    )

    updated_at = DateTimeField(
        verbose_name=_('Date of update'),
        auto_now=True,
        null=True,
    )

    class Meta:
        abstract = True


class ChannelsMixin(Model):
    channels = ManyToManyField(
        'Channel',
        verbose_name=_('Channels'),
    )

    class Meta:
        abstract = True


class ImageMixin(Model):
    image = ImageField(
        null=True,
        blank=True,
        verbose_name=_('Image'),
    )

    def save(self, *args, **kwargs):
        if not self.image:
            self.image.name = get_default_telegram_image()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class AdminImageMixin:
    def preview_image(self, obj):
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="75" style="border-radius: 50%;">')
        else:
            return _('[Image not set]')

    preview_image.short_description = _('Image')

    def get_list_display(self, request):
        return (*super().get_list_display(request), 'preview_image')


class MediaGalleryMixin:
    class Media:
        js = (
            'assets/vendor/js/jquery-3.7.0.min.js',
            'assets/js/admin/gallery.js',
        )
