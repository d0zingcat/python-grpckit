import os
from typing import Dict, Optional, Callable, List, Type, Any
from collections import defaultdict
from types import MappingProxyType

import grpc
from concurrent.futures import ThreadPoolExecutor

from grpckit.constant import (
    K_GRPCKIT_DEBUG,
    K_GRPCKIT_MAX_WORKERS,
    K_GRPCKIT_TLS_CA_CERT,
    K_GRPCKIT_SERVICE_SCAN_DIR,
    K_GRPCKIT_TLS_SERVER_KEY,
    K_GRPCKIT_TLS_SERVER_CERT,
)
from grpckit.config import Config
from grpckit.service import Service
from grpckit.interceptor import MiddlewareInterceptor, RpcExceptionInterceptor
from grpckit.utils.proto import scan_pb_grpc


class GrpcKitApp:

    # store all services registered
    _services: Dict[str, Service] = {}

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

        self.exc_handler_spec: Dict[
            Optional[str], Dict[Type[Exception], Callable]
        ] = defaultdict(lambda: defaultdict(dict))

        self.teardown_app_context_funcs: List[Callable] = []

    def run(
        self, host: Optional[str] = None, port: Optional[int] = None, **kwargs: Any
    ) -> None:
        options = self.config.rpc_options()

        # With RpcExceptionInterceptor as the most inner interceptor,
        # this ensures all the exceptions will be caught and process to
        # normal grpc response, and the @after_request funcs will always be invoked.
        # There is no need to worry about resource leak, in case that the
        # after_request func itself would not cause exception at all.
        interceptors = (
            MiddlewareInterceptor(
                self.before_request_funcs.get(None, ()),
                self.after_request_funcs.get(None, ()),
            ),
            *self.interceptors.get(None, ()),
            RpcExceptionInterceptor(),
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
        self._register_funcs = scan_pb_grpc(
            path=self.config.get(K_GRPCKIT_SERVICE_SCAN_DIR, ".")
        )

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
            print(func, instance)
            func(instance, server)
