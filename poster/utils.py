from os import path

from django.conf import settings
from django.utils.safestring import mark_safe
from markdownify import abstract_inline_conversion
from markdownify import MarkdownConverter

from telegram_bot import TelegramBot


def save_file(name: str, content: bytes) -> None:
    with open(path.join(settings.MEDIA_ROOT, name), mode='wb') as file:
        file.write(content)


def download_channel_photo(channel: 'Channel', file_id: str) -> None:  # NOQA: F821 # type: ignore
    content = TelegramBot(channel.bot.token).download_file_from_telegram(file_id)
    if content:
        channel.image.name = file_id
        save_file(file_id, content)


class BaseMarkdownConverter(MarkdownConverter):
    def convert_p(self, el, text, convert_as_inline):
        text = super().convert_p(el, text, convert_as_inline)
        if not text:
            return ''
        return text.replace('\n\n', '\n')


class TelegramMarkdownConverter(BaseMarkdownConverter):
    convert_em = abstract_inline_conversion(lambda self: '_')
    convert_u = abstract_inline_conversion(lambda self: '__')
    convert_s = abstract_inline_conversion(lambda self: '~')
    convert_strong = abstract_inline_conversion(lambda self: '*')


class DiscordMarkdownConverter(BaseMarkdownConverter):
    pass


def escape_chars(message: str) -> str:
    chars = ['_', '*', '[', ']', '(', ')', '~', '`', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in chars:
        message = message.replace(char, f'\\{char}')
    return message


def escape_telegram_message(message: str) -> str:
    return TelegramMarkdownConverter(bullets='-').convert(escape_chars(message))


def escape_discord_message(message: str) -> str:
    return DiscordMarkdownConverter(bullets='-').convert(escape_chars(message))


def get_default_channel_image(messenger):
    return path.join('default', f'{messenger}_channel_icon.png')


def render_attachments(files: list | None) -> str:
    html = ''

    if not files:
        return html

    for file in files:
        ext = file.name.split('.')[-1] if hasattr(file, 'name') else file.file.name.split('.')[-1]
        url = file.url if hasattr(file, 'name') else file.file.url

        if ext in ('png', 'jpg', 'jpeg'):
            html += f'<img class="photo" src="{url}"></img>'
        else:
            html += f'<a class="file" href="{url}"><img src="/media/default/download.png"></img></a>'

    return html


def prepare_markup(message: str | None = None, files: list | None = None) -> str:
    return mark_safe(
        f'''<div class="post-content">
            <div class="attachment">
                {render_attachments(files)}
            </div>
            <div class="message">
                {message or ''}
            </div>
        </div>'''
    )
