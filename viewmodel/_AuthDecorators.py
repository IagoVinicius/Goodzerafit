from typing import Callable


def need_jwt(fn: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        self = args[0]

        if not self.request.headers.get('Authorization'):
            raise Exception

        return fn(*args, **kwargs)

    return wrapper
