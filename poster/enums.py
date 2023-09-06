from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


class PostTypeEnum(TextChoices):
    AUDIO = 'audio', _('Audio message')
    DOCUMENT = 'document', _('Document message')
    GALLERY_DOCUMENTS = 'gallery_documents', _('Gallery documents')
    GALLERY_PHOTOS = 'gallery_photos', _('Gallery photos')
    TEXT = 'text', _('Text message')
    PHOTO = 'photo', _('Photo message')
    VIDEO = 'video', _('Video message')
    VOICE = 'voice', _('Voice message')


class RecordTypeEnum(TextChoices):
    CREATE = 'create', _('CREATE')
    UPDATE = 'update', _('UPDATE')
    DELETE = 'delete', _('DELETE')
    UNKNOWN = 'unknown', _('UNKNOWN')
