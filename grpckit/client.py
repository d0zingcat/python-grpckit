from contextlib import contextmanager
import re

import grpc

from .common import ContextManager
from .types import GrpcKitResponse, WrappedDict
from .utils.proto import scan_pb_grpc
from .utils.parser import DictToMessage, MessageToDict


class MethodWrapper:
    def __init__(
        self,
        method,
        channel,
        name,
        stub_name,
        reuse_channel,
        pb_request_models,
        timeout=None,
    ):
        self._method = method
        self._channel = channel
        self._reuse_channel = reuse_channel
        self._pb_request_models = pb_request_models
        self._name = name
        self._stub_name = stub_name
        self._timeout = timeout

    def __call__(self, **kwargs):
        args = kwargs.pop("_args", {})
        response_pb = args.pop("response_pb", None)
        request_pb = args.pop("request_pb", None)
        _name_split = re.split(r"Stub$", self._stub_name)
        if not _name_split:
            raise ValueError("Invalid stub!")
        _name = _name_split[0]
        request_import_format = f"{_name}__pb2.{self._name}_request"
        response_import_format = f"{_name}__pb2.{self._name}_response"
        if not request_pb:
            request_pb = self._pb_request_models.get(request_import_format)
        if not response_pb:
            response_pb = self._pb_request_models.get(response_import_format)
        if not request_pb:
            raise ValueError("Invalid pb request")
        if not response_pb:
            raise ValueError("Invalid pb response")

        if self._timeout is not None:
            args["timeout"] = self._timeout
        request = DictToMessage(kwargs, request_pb())
        grpckit_response = GrpcKitResponse()
        try:
            response = self._method(request=request, **args)
            grpckit_response.load_data(response)
        except grpc.RpcError as e:
            if e.code() != grpc.StatusCode.OK:
                grpckit_response.ok = False
                grpckit_response.msg = e.details()
            # raise exception by default
            raise
        finally:
            # 不重用channel则关闭
            if not self._reuse_channel:
                self._channel._close()
        return WrappedDict.convert_from_dict(MessageToDict(response))


class GrpcKitClient:
    def __init__(
        self,
        target,
        grpc_stub,
        transparent_transform=True,
        reuse_channel=False,
        scan_dir="./protos/pb",
        credentials=None,
        timeout=None,
    ):
        self._secure = False
        self._channel = None
        self._pb_request_models = dict()

        self._transparent_transform = transparent_transform
        self._scan_dir = scan_dir
        self._reuse_channel = reuse_channel
        if credentials:
            self._secure = True
            self._credentials = credentials
        self._stub = grpc_stub
        self._stub_name = grpc_stub.__name__
        if len(target.split(":")) != 2:
            raise ValueError("Invalid target, should be like localhost:50051")
        self._target = target
        _register_funcs, pb_request_models = scan_pb_grpc(
            path=scan_dir,
            import_request_model=True,
        )
        for k, v in pb_request_models.items():
            self._pb_request_models[k] = v
        self._timeout = timeout

    @property
    def channel(self):
        if self._reuse_channel and self._channel is not None:
            return self._channel
        channel = self._get_channel()
        if self._reuse_channel:
            self._channel = channel
        return channel

    def _get_channel(self):
        if self._secure:
            return grpc.secure_channel(self._target, credentials=self._credentials)
        else:
            return grpc.insecure_channel(self._target)

    def __getattr__(self, name):
        channel = self.channel
        stub = self._stub(channel)
        return MethodWrapper(
            getattr(stub, name),
            channel,
            name,
            self._stub_name,
            self._reuse_channel,
            self._pb_request_models,
            timeout=self._timeout,
        )


class ClientContext(ContextManager):
    def __init__(self, target, credentials=None):
        self.secure = False
        if credentials:
            self.secure = True
        if len(target.split(":")) != 2:
            raise ValueError("Invalid target, should be like localhost:50051")
        self.target = target
        self().__init__(target, credentials=credentials)

    @contextmanager
    def contextmanager(self):
        if self.secure:
            try:
                with grpc.secure_channel(self.target) as channel:
                    yield channel
            finally:
                pass
        else:
            try:
                with grpc.insecure_channel(self.target) as channel:
                    yield channel
            finally:
                pass
