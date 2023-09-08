from os import path

from django.conf import settings
from markdownify import abstract_inline_conversion
from markdownify import MarkdownConverter


def save_file(name: str, content: bytes) -> None:
    with open(path.join(settings.MEDIA_ROOT, name), mode='wb') as file:
        file.write(content)


class TelegramMarkdownConverter(MarkdownConverter):
    convert_em = abstract_inline_conversion(lambda self: '_')
    convert_u = abstract_inline_conversion(lambda self: '__')
    convert_s = abstract_inline_conversion(lambda self: '~')
    convert_strong = abstract_inline_conversion(lambda self: '*')

    def convert_p(self, el, text, convert_as_inline):
        text = super().convert_p(el, text, convert_as_inline)
        if not text:
            return ''
        return text.replace('\n\n', '\n')


def prepare_message(message: str) -> str:
    message = TelegramMarkdownConverter(bullets='-').convert(message)
    message = message.replace('.', '\\.')
    message = message.replace('-', '\\-')
    return message


def get_default_telegram_image():
    return path.join('default', 'telegram_icon.jpg')
