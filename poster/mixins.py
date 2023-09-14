from typing import Any
from django.contrib.admin import ModelAdmin
from django.core.handlers.wsgi import WSGIRequest
from django.db.models import DateTimeField
from django.db.models import ImageField
from django.db.models import ManyToManyField
from django.db.models import Model
from django.utils.translation import gettext_lazy as _
from django.utils.safestring import mark_safe

from .utils import get_default_telegram_image


class BaseMixin(Model):
    created_at: DateTimeField = DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name=_('Date of creation'),
    )

    updated_at: DateTimeField = DateTimeField(
        auto_now=True,
        null=True,
        verbose_name=_('Date of update'),
    )

    class Meta:
        abstract = True


class ChannelsMixin(Model):
    channels: ManyToManyField = ManyToManyField(
        'Channel',
        verbose_name=_('Channels'),
    )

    class Meta:
        abstract = True


class ImageMixin(Model):
    image: ImageField = ImageField(
        null=True,
        blank=True,
        verbose_name=_('Image'),
    )

    def save(self, *args, **kwargs) -> None:
        if not self.image:
            self.image.name = get_default_telegram_image()
        return super().save(*args, **kwargs)

    class Meta:
        abstract = True


class AdminImageMixin(ModelAdmin):
    def preview_image(self, obj: Any) -> str:
        if obj.image:
            return mark_safe(f'<img src="{obj.image.url}" width="75" style="border-radius: 50%;">')
        else:
            return '[Image not set]'

    preview_image.short_description = _('Image')

    def get_list_display(self, request: WSGIRequest) -> list:
        return [*super().get_list_display(request), 'preview_image']


class MediaGalleryMixin:
    class Media:
        js = (
            'assets/vendor/js/jquery-3.7.0.min.js',
            'assets/js/admin/gallery.js',
        )
