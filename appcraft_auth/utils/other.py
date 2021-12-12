import re
from functools import reduce

from django.conf import settings


def chained_get(obj, *args, default=None):
    def get_value(o, attr):
        if isinstance(o, dict) and (isinstance(attr, str) or attr is None):
            return o.get(attr, default)
        if isinstance(o, (list, tuple)) and isinstance(attr, int):
            return o[attr]
        if isinstance(o, object) and isinstance(attr, str):
            return getattr(o, attr, default)
        return None

    try:
        result = reduce(get_value, args, obj)
        return result
    except Exception as e:
        return default


def nonefy(value, condition=True):
    if condition:
        return None
    return value


def has_latin(text: str = None):
    if text and isinstance(text, str):
        return bool(re.search('[a-zA-Z]', text))
    return False


def get_code_max_length():
    try:
        return settings.APPCRAFT_AUTH_EMAIL_SETTINGS.get('CODE_LENGTH', 4)
    except AttributeError:
        return 4
