from os import path
from re import search
from re import DOTALL

from django.conf import settings


def save_file(name: str, content: bytes) -> None:
    with open(path.join(settings.MEDIA_ROOT, name), mode='wb') as file:
        file.write(content)


def clean_message(message: str) -> str:
    message = message.replace('<br>', '')
    group = search(r'<p>(.*?)</p>', message, DOTALL)
    return group.group(1) if group else message
