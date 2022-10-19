from typing import Optional, Callable, Dict, Any
from functools import partial, wraps
from inspect import getfullargspec, isfunction

import grpc


from .utils.parser import MessageToDict, DictToMessage
from .types import WrappedDict


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
                    # response_pb/request_pb is optional, if not passed
                    # will read response from current app domain
                    # response format is "{service.name}__pb2.{func.name}_response"
                    # request format is "{service.name}__pb2.{func.name}_request"
                    if not response_pb:
                        # HACK: stateful method which gets data from current_app obj
                        from .globals import current_app

                        response_pb_name = f"{self.name}__pb2.{func.__name__}_response"
                        request_pb_name = f"{self.name}__pb2.{func.__name__}_request"
                        _response_pb = current_app._pb_request_models.get(
                            response_pb_name
                        )
                        _request_pb = current_app._pb_request_models.get(
                            request_pb_name
                        )
                    else:
                        _response_pb = response_pb
                        _request_pb = request_pb
                    if not _request_pb:
                        raise ValueError("Invalid request_pb!")
                    if not _response_pb:
                        raise ValueError("Invalid response_pb!")
                    request = WrappedDict(MessageToDict(request))
                    response = func(request, context)
                    if type(response) is not dict:
                        raise AssertionError("Response must be python dict!")
                    return DictToMessage(response, _response_pb())
                response = func(request, context)
                return response

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
