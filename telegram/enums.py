from django.db.models import TextChoices


class BotActionTypeEnum(TextChoices):
    TYPING = 'typing'
    UPLOAD_AUDIO = 'upload_audio'
    UPLOAD_DOCUMENT = 'upload_document'
    UPLOAD_PHOTO = 'upload_photo'
    UPLOAD_VIDEO = 'upload_video'
    UPLOAD_VOICE = 'upload_voice'
