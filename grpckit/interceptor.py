from functools import wraps
from typing import Callable, List, Type, Dict
import traceback

from .exception import RpcException
from .pb import default_pb2

from grpc import ServerInterceptor, StatusCode
from grpc.experimental import wrap_server_method_handler


class BaseInterceptor(ServerInterceptor):
    ...


class MiddlewareInterceptor(BaseInterceptor):
    def __init__(
        self,
        before_request_chains: List[Callable],
        after_request_chains: List[Callable],
    ) -> None:
        """Middleware Interceptor"""
        self.before_request_chains = before_request_chains
        self.after_request_chains = after_request_chains

    def _wrapper(self, behavior):
        @wraps(behavior)
        def wrapper(request, context):
            # Ignore method request for reflection
            method = context._rpc_event.call_details.method
            if (
                method.decode()
                == "/grpc.reflection.v1alpha.ServerReflection/ServerReflectionInfo"
            ):
                return behavior(request, context)

            # process pre processors one by one
            for chain in self.before_request_chains:
                resp = chain(request, context)
                if resp:
                    return resp
            # actual working func
            response = behavior(request, context)
            # process post processors one by one
            for chain in self.after_request_chains:
                response = chain(response)
                if not response:
                    raise ValueError(
                        "Miss response from after response interceptor: %s"
                        % chain.__name__
                    )
            return response

        return wrapper

    def intercept_service(self, continuation, handler_call_details):
        return wrap_server_method_handler(
            self._wrapper, continuation(handler_call_details)
        )


class RpcExceptionInterceptor(BaseInterceptor):
    """Global RpcException Interceptor, which intercepts all exceptions.
    Wraps status code and msg to gRPC header.
    :param exc_handlers is a dict whose signature is func(exception, grpc_context)
    """

    def __init__(  # pylint: disable=super-init-not-called
        self, app, exc_handlers: Dict[Type[Exception], Callable] = None
    ) -> None:
        self.app = app
        self._exc_handlers = exc_handlers or dict()

    def _default_handler(self, e, context):
        context.set_code(StatusCode.INTERNAL)
        context.set_details("Internal Error")
        return default_pb2.Empty()

    def _wrapper(self, behavior):
        @wraps(behavior)
        def wrapper(request, context):
            ctx = self.app.request_context(request, context)
            try:
                ctx.push()
                return behavior(request, context)
            except Exception as e:
                # if debug, raise exception directly
                if self.app.debug:
                    context.set_code(StatusCode.INTERNAL)
                    context.set_details(traceback.format_exc())
                    raise
                # If the exception is instantiated from RpcException,
                # use the code and details directly.
                # NOTE: Maybe it's a good choice to give permission to choose
                # whether to raise exception or catch all exceptions,
                # but to achieve this goal, the teardown_request feature must be
                # completed firstly.
                if isinstance(e, RpcException):
                    context.set_code(e.status_code)
                    context.set_details(e.details)
                    return default_pb2.Empty()
                else:
                    # common exceptions would defauld to RpcException
                    for cls in type(e).mro():
                        handler = self._exc_handlers.get(cls)
                        if handler and callable(handler):
                            return handler(e, context)
                    # use default handler
                    return self._default_handler(e, handler)
            finally:
                ctx.pop()

        return wrapper

    def intercept_service(self, continuation, handler_call_details):
        return wrap_server_method_handler(
            self._wrapper, continuation(handler_call_details)
        )
