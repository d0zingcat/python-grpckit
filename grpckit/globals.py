from typing import Dict
from functools import partial
from .local import LocalProxy, LocalStack


_request_ctx_stack = LocalStack()
_app_ctx_stack = LocalStack()


def _lookup_req_object(name):
    top = _request_ctx_stack.top
    if top is None:
        raise RuntimeError("Working outside of request context")
    return getattr(top, name)


def _lookup_app_object(name):
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError("Working outside of application context")
    return getattr(top, name)


def _find_app():
    top = _app_ctx_stack.top
    if top is None:
        raise RuntimeError("Working outside of application context")
    return top.app


current_app = LocalProxy(_find_app)
request = LocalProxy(partial(_lookup_req_object, "request"))
g: Dict = LocalProxy(partial(_lookup_app_object, "g"))
