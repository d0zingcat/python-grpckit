import sys
from typing import Optional, List

from .globals import (
    _app_ctx_stack,
    _request_ctx_stack,
)
from .wrapper import Request

# a singleton sentinel value for parameter defaults
_sentinel = object()


class AppContext:
    """Application context"""

    def __init__(self, app) -> None:
        self.app = app
        self.g = {}

        self._ref_cnt = 0

    def push(self) -> None:
        self._ref_cnt += 1
        _app_ctx_stack.push(self)

    def pop(self, exc: Optional[BaseException] = _sentinel) -> None:
        try:
            self._ref_cnt -= 1
            if self._ref_cnt <= 0:
                if exc is _sentinel:
                    exc = sys.exc_info()[1]
                self.app.do_teardown_app_context(exc)
        finally:
            _app_ctx_stack.pop()

    def __enter__(self) -> "AppContext":
        self.push()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.pop(exc_val)


class RequestContext:
    def __init__(self, app, params=None, context=None) -> None:
        """Create request context"""
        self.app = app
        self.request = Request(params, context)

        self._implicit_app_ctx_stack: List[Optional[AppContext]] = []

        self.preserved = False
        self._preserved_exc = None

    def push(self) -> None:
        """Push request context"""
        top = _request_ctx_stack.top
        if top is not None and top.preserved:
            top.pop(top._preserved_exc)

        # read context of current thread
        app_ctx = _app_ctx_stack.top
        if app_ctx is None or app_ctx.app != self.app:
            app_ctx = self.app.app_context()
            app_ctx.push()
            self._implicit_app_ctx_stack.append(app_ctx)
        else:
            self._implicit_app_ctx_stack.append(None)

        _request_ctx_stack.push(self)

    def pop(self, exc: Optional[BaseException] = _sentinel) -> None:
        """Pop request context"""
        app_ctx = self._implicit_app_ctx_stack.pop()
        try:
            if not self._implicit_app_ctx_stack:
                self.preserved = False
                self._preserved_exc = None
                self.app.do_teardown_request(exc)

        finally:
            rv = _request_ctx_stack.pop()

            if app_ctx is not None:
                app_ctx.pop(exc)

            if rv is not self:
                raise RuntimeError("Popped wrong request context")

    def __enter__(self) -> "RequestContext":
        self.push()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.pop(exc_val)
