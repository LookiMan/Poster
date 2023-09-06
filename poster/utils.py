from typing import Optional
from typing import List

from os import path

from re import search
from re import DOTALL

from django.conf import settings
from django.core.cache import cache


Serializable = Optional[str | bool | int | float | list | dict | tuple | None]


def save_file(name: str, content: bytes) -> None:
    with open(path.join(settings.MEDIA_ROOT, name), mode='wb') as file:
        file.write(content)


def clean_message(message: str) -> str:
    message = message.replace('<br>', '')
    group = search(r'<p>(.*?)</p>', message, DOTALL)
    return group.group(1) if group else message


def create_redis_key(namespace: List[str | int]) -> str:
    return '::'.join([str(name) for name in namespace])


def cache_set(namespace: List[str | int], *, value: Serializable, timeout: int) -> None:
    cache.set(create_redis_key(namespace), value=value, timeout=timeout)


def cache_get(namespace: List[str | int]) -> Optional[Serializable]:
    return cache.get(create_redis_key(namespace))


def cache_pop(namespace: List[str | int]) -> Optional[Serializable]:
    tag = create_redis_key(namespace)
    info = cache.get(tag)
    if info:
        cache.delete(tag)
    return info
