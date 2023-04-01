import json
from collections.abc import Iterable
import base64
from datetime import datetime
from typing import Union
from bson import ObjectId


def format(obj, load_obj=None):
    new_obj = obj if isinstance(obj, Iterable) else {}
    convert = dict(load_obj if load_obj else new_obj)
    return dict({'id': obj.id} if hasattr(obj, 'id') else {}, **convert)


def serialize(
            obj: Union[dict, list],
            fields: list = None) -> str:
    def to_serialize(y):
        if isinstance(y, datetime):
            return y.isoformat()

        if isinstance(y, bytes):
            try:
                return y.decode('utf-8')
            except UnicodeError:
                return base64.b64encode(y).decode('utf-8')
            except Exception:
                return ''

        if isinstance(y, ObjectId):
            return str(y)


    def fields_only(d):
        return {k: v for (k, v) in d.items() if k in fields}

    def dict_loop(y):
        return fields_only(y.__dict__) if len(fields) else {}

    def convert(y):
        return to_serialize(y) or dict_loop(y)

    return json.dumps(obj, **dict({'default': convert, 'separators': (',', ':')}))


def sanitize(obj, fields, exclude=None, get_original_object=False):
    if not obj:
        return

    serialized = obj

    try:
        if not isinstance(obj, (int, str, bytes)):
            serialized = serialize(format(obj), fields=fields)

        sanitized = json.loads(serialized)

        if exclude:
            [sanitized.pop(x, None) for x in exclude]

        if fields:
            [sanitized.pop(x, None) for x in list(set(sanitized.keys()) - set(fields))]

        if get_original_object:
            return sanitized, serialized

        return sanitized
    except Exception as ex:
        return ex