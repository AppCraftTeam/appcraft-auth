import re


def chained_get(obj, *args, default=None):
    def get_value(o, attr):
        if isinstance(o, dict) and (isinstance(attr, str) or attr is None):
            return o.get(attr, default)
        if isinstance(o, (list, tuple)) and isinstance(attr, int):
            return o[attr]
        if isinstance(o, object) and isinstance(attr, str):
            return getattr(o, attr, default)
        return None


def nonefy(value, condition=True):
    if condition:
        return None
    return value


def has_latin(text: str = None):
    if text and isinstance(text, str):
        return bool(re.search('[a-zA-Z]', text))
    return False
