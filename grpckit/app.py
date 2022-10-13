from typing import Dict, Optional, Callable, List, Any
from collections import defaultdict
from types import MappingProxyType
from concurrent.futures import ThreadPoolExecutor
import os
import sys

import grpc

from .constant import (
    K_GRPCKIT_DEBUG,
    K_GRPCKIT_MAX_WORKERS,
    K_GRPCKIT_TLS_CA_CERT,
    K_GRPCKIT_SERVICE_SCAN_DIR,
    K_GRPCKIT_TLS_SERVER_KEY,
    K_GRPCKIT_TLS_SERVER_CERT,
)
from .config import Config
from .service import Service
from .interceptor import MiddlewareInterceptor, RpcExceptionInterceptor
from .ctx import AppContext, RequestContext
from .utils.proto import scan_pb_grpc


# a singleton sentinel value for parameter defaults
_sentinel = object()


class GrpcKitApp:

    # store all services registered
    _services: Dict[str, Service] = dict()

    # store all pb request models
    _pb_request_models: Dict[str, Any] = dict()

    default_config = MappingProxyType(
        {
            K_GRPCKIT_MAX_WORKERS: 10,
            K_GRPCKIT_DEBUG: False,
            K_GRPCKIT_SERVICE_SCAN_DIR: ".",
        }
    )

    def __init__(self, name=None):
        self.name: str = name or "grpckit"
        self.config: Config = Config(self.default_config)

        self.services: Dict[str, Service] = dict()

        self.before_request_funcs: Dict[Optional[str], List[Callable]] = defaultdict(
            list
        )

        self.after_request_funcs: Dict[Optional[str], List[Callable]] = defaultdict(
            list
        )

        self.interceptors = {}

        self.teardown_app_context_funcs: List[Callable] = []

    def run(
        self, host: Optional[str] = None, port: Optional[int] = None, **kwargs: Any
    ) -> None:
        options = self.config.rpc_options()

        """With RpcExceptionInterceptor as the most inner interceptor,
        this ensures all the exceptions will be caught and process to
        normal grpc response, and the @after_request funcs will always be invoked.
        There is no need to worry about resource leak, in case that the
        after_request func itself would not cause exception at all.
        Server side interceptor principal
        clipped from [L13-python-interceptors.md](https://github.com/grpc/proposal/blob/master/L13-python-interceptors.md#server-side-implementation) # noqa: E501
        Server Receives a Request ->
        Interceptor A Start ->
            Interceptor B Start ->
                Interceptor C Start ->
                    The Original Handler
                Interceptor C Returns Updated Handler C ->
            Interceptor B Returns Updated Handler B ->
        Interceptor A Returns Updated Handler A ->

        Invoke the Updated Handler A with the Request ->
        Updated Handler A Returns Response ->
        """
        interceptors = (
            RpcExceptionInterceptor(self),
            MiddlewareInterceptor(
                self.before_request_funcs.get(None, ()),
                self.after_request_funcs.get(None, ()),
            ),
            *self.interceptors.get(None, ()),
        )

        max_workers = self.config.get(K_GRPCKIT_MAX_WORKERS, 10)

        server = grpc.server(
            ThreadPoolExecutor(max_workers=max_workers),
            interceptors=interceptors,
            options=options,
        )

        # Bind service to gRPC server
        self._bind_service(server)
        # Enable health checking
        # self._enable_health(server)

        address = "%s:%s" % (host or "[::]", port or 50051)
        server = self._bind_port(server, address, **kwargs)
        server.start()
        print("start server", address)

        # self.log.info(
        #     f"Running on {address} (Press CTRL+C to quit)"
        # )  # pylint: disable=no-member
        server.wait_for_termination()
        # self.log.info("gRPC server stopped!")

    def before_request(self, func: Callable) -> Callable:
        self.before_request_funcs.setdefault(None, []).append(func)
        return func

    def after_request(self, func: Callable) -> Callable:
        self.after_request_funcs.setdefault(None, []).append(func)
        return func

    def _bind_port(
        self, server: grpc.Server, address: str, **options: Any
    ) -> grpc.Server:
        def _read_pem(path):
            if path is None:
                return path

            if not os.path.exists(path):
                raise FileExistsError("server tls file not exists at: %s" % path)

            with open(path, "rb") as f:
                return f.read()

        # Support TLS server
        server_cert = options.get(K_GRPCKIT_TLS_SERVER_CERT.lower()) or self.config.get(
            K_GRPCKIT_TLS_SERVER_CERT
        )
        server_key = options.get(K_GRPCKIT_TLS_SERVER_KEY.lower()) or self.config.get(
            K_GRPCKIT_TLS_SERVER_KEY
        )

        # also support ca cert
        ca_cert = options.get(K_GRPCKIT_TLS_CA_CERT.lower()) or self.config.get(
            K_GRPCKIT_TLS_CA_CERT
        )

        if not server_cert or not server_key:
            server.add_insecure_port(address)
            return server

        credentials = grpc.ssl_server_credentials(
            [(_read_pem(server_key), _read_pem(server_cert))],
            root_certificates=_read_pem(ca_cert),
            require_client_auth=bool(ca_cert),
        )
        server.add_secure_port(address, credentials)
        return server

    def register_service(self, service: Service) -> None:
        if not service or not isinstance(service, Service):
            raise ValueError("Invalid service to register!")

        if self._services.get(service.name):
            raise AssertionError(f"Service is overwriting and existing: {service.name}")

        self._services[service.name] = service

    def legacy_route(
        self, method: Optional[str] = None, service: Optional[str] = None
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            if not service:
                raise ValueError(f"Invalid service name for method: {method}")

            s = self._services.get(service)
            if not s:
                s = Service(name=service)

            s.add_method_rule(method, func)
            self._services[service] = s
            return func

        return decorator

    def route(
        self, func: Optional[Callable] = None, service: Optional[str] = None
    ) -> Callable:
        def decorator(func: Callable) -> Callable:
            method = func.__name__
            if not service:
                raise ValueError(f"Invalid service name for method: {method}")

            s = self._services.get(service)
            if not s:
                s = Service(name=service)

            s.add_method_rule(method, func)
            self._services[service] = s

            if not func:
                raise ValueError("Invalid func! Func should not be None")
            self.add_method_rule(func.__name__, func)
            return func

        if func is None:
            return decorator
        return decorator(func)

    def _bind_service(self, server: grpc.Server) -> None:
        register_funcs, pb_request_models = scan_pb_grpc(
            path=self.config.get(K_GRPCKIT_SERVICE_SCAN_DIR, "."),
            import_request_model=True,
        )

        self._register_funcs = register_funcs
        for name, instance in self._services.items():
            if not isinstance(instance, Service):
                raise TypeError(
                    f"Service instance type must be `Service`, Please check: {name}"
                )

            func = self._register_funcs.get("add_%sServicer_to_server" % name)
            if not func:
                raise ValueError(
                    f"Can't find service '{name}' info from ProtoBuf files!"
                )
            # Use add_xServicer_to_server function in ProtoBuf to bind
            # service to gRPC server
            func(instance, server)
            for k, v in pb_request_models.items():
                self._pb_request_models[k] = v

    @property
    def debug(self) -> bool:
        return self.config[K_GRPCKIT_DEBUG]

    @debug.setter
    def debug(self, value: bool) -> None:
        self.config[K_GRPCKIT_DEBUG] = value

    def request_context(self, params, context):
        return RequestContext(self, params, context)

    def app_context(self):
        return AppContext(self)

    def do_teardown_app_context(self, exc: Optional[BaseException] = None) -> None:
        """Called right before the application context is popped"""
        if exc is _sentinel:
            exc = sys.exc_info()[1]
        for func in reversed(self.teardown_app_context_funcs):
            func(exc)
