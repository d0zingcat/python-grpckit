from typing import Optional, Callable, Dict, Any
from functools import partial, wraps
from inspect import getfullargspec, isfunction

import grpc


from grpckit.utils.parser import MessageToDict, DictToMessage


class Service:

    _router: Dict[str, Callable] = dict()

    def __init__(self, name: str, router: Optional[Dict[str, Callable]] = None) -> None:
        # The name of service, this value must be the same as the value in ProtoBuf
        self.name = name

        if router and isinstance(router, dict):
            for method, func in router.items():
                self.add_method_rule(method, func)

    def legacy_route(self, method: Optional[str] = None) -> Callable:
        """Legacy way to add new route for service"""

        def decorator(func: Callable) -> Callable:
            self.add_method_rule(method, func)
            return func

        return decorator

    def route(self, func: Optional[Callable] = None) -> Callable:
        """Add new route for service"""

        def decorator(func: Callable) -> Callable:
            if not func:
                raise ValueError("Invalid func! Func should not be None")
            self.add_method_rule(func.__name__, func)
            return func

        if func is None:
            return decorator
        return decorator(func)

    def armed(
        self,
        func: Optional[Callable] = None,
        *,
        request_pb: Any = None,
        response_pb: Any = None,
        transparent_transform: bool = True,
    ) -> Callable:
        """Add new route for service and parse request/response"""

        def decorator(func: Callable) -> Callable:
            if not func:
                raise ValueError("Invalid func! Func should not be None")

            @wraps(func)
            def wrapper(request, context):
                if transparent_transform:
                    request = MessageToDict(request)
                    response = func(request, context)
                    if not response_pb:
                        raise ValueError("Invalid response_pb!")
                    if type(response) is not dict:
                        raise AssertionError("Response must be python dict!")
                    return DictToMessage(response, response_pb())

            self.add_method_rule(wrapper.__name__, wrapper)
            return wrapper

        if func is None:
            return decorator
        return decorator(func)

    def add_method_rule(
        self, method: Optional[str] = None, func: Optional[Callable] = None
    ) -> Any:
        """Add new method handler rule"""
        if not method or not func:
            raise ValueError("Invalid method name or handler func")

        if not isfunction(func) or not callable(func):
            raise ValueError(f"Callback func '{method}' is not callable!")

        old_func = self._router.get(method)
        if old_func is not None and old_func != func:
            raise AssertionError(f"Method is overwriting and existing: {method}")

        self._router[method] = func

    def _not_implement_method(self, context):
        """Handler for not implement method"""
        context.set_code(grpc.StatusCode.NOT_FOUND)
        context.set_details("Method not fund!")
        raise NotImplementedError("Method not fund!")

    def _default_handler(self, request, context, **kwargs):
        """Default handler"""
        func = self._router.get(kwargs["func"], self._not_implement_method)
        args = getfullargspec(func).args

        options = {}
        if "request" in args:
            options["request"] = request
        if "context" in args:
            options["context"] = context

        return func(**options)

    def __getattr__(self, item):
        return partial(self._default_handler, func=item)
