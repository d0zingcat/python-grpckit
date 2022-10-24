import sys
from inspect import isbuiltin

import grpc

from .._internal import _Missing


_missing = _Missing()


class cached_property(property):
    """A decorator that converts a function into a lazy property.
    The function wrapped is called the first time to retrieve the result
    and then that calculated result is used the next time you access the value"""

    def __init__(self, func, name=None, doc=None):  # pylint: disable=super-init-not-called
        self.__name__ = name or func.__name__
        self.__module__ = func.__module__
        self.__doc__ = doc or func.__doc__
        self.func = func

    def __set__(self, obj, value):
        obj.__dict__[self.__name__] = value

    def __get__(self, obj, tp=None):
        if obj is None:
            return self

        value = obj.__dict__.get(self.__name__, _missing)
        if value is _missing:
            value = self.func(obj)
            obj.__dict__[self.__name__] = value
        return value


_RPC_BUILTIN_KEYS = {
    "Extensions",
    "DESCRIPTOR",
    "_SetListener",
    "_extensions_by_name",
    "_extensions_by_number",
}


def deserialize_request(obj):
    """Deserialize gRPC request"""
    if isinstance(obj, grpc._server._RequestIterator):
        fmt_rst = list()
        for item in obj:
            fmt_rst.append(deserialize_request(item))
        return fmt_rst

    # do nothing about non grpc generated obj
    if not hasattr(obj, "DESCRIPTOR"):
        return obj

    fmt_rst = {}
    for key in dir(obj):
        # skip inner property
        if key.startswith("__") or key in _RPC_BUILTIN_KEYS or not hasattr(obj, key):
            continue

        val = getattr(obj, key)
        # skip builtin in property
        if isbuiltin(val):
            continue

        # deserialize recursively
        if isinstance(val, (list, tuple, set)):
            val = [deserialize_request(v) for v in val]
        elif hasattr(val, "DESCRIPTOR"):
            val = deserialize_request(val)

        fmt_rst[key] = val

    return fmt_rst


def import_string(import_name):
    import_name = str(import_name).replace(":", ".")
    try:
        __import__(import_name)
    except ImportError:
        if "." not in import_name:
            raise
    else:
        return sys.modules[import_name]

    module_name, obj_name = import_name.rsplit(".", 1)
    module = __import__(module_name, None, None, [obj_name])
    try:
        return getattr(module, obj_name)
    except AttributeError as e:
        raise ImportError(e)


def logger_has_level_handler(logger):
    """Check if there is a handler in the logging chain that will handle the
    given logger's effective level
    """
    level = logger.getEffectiveLevel()
    current = logger

    while current:
        if any(handler.level <= level for handler in current.handlers):
            return True

        if not current.propagate:
            break

        current = current.parent

    return False
