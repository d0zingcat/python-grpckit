from functools import wraps
from typing import Callable, List

from grpc import ServerInterceptor
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
