from django.db.models import DateTimeField
from django.db.models import ManyToManyField
from django.db.models import Model
from django.utils.translation import gettext_lazy as _


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
