from contextlib import contextmanager

import grpc

from .common import ContextManager


class BaseClient:
    def __init__(
        self,
        target,
        credentials=None,
    ):
        self.secure = False
        if credentials:
            self.secure = True
        if len(target.split(":")) != 2:
            raise ValueError("Invalid target, should be like localhost:50051")
        self.target = target
        self().__init__()


class GrpcKitClient(BaseClient):
    def __init__(self, pb_grpc=None, *args, **kwargs):
        self.__init__(*args, **kwargs)

    def __getattribute__(self, name):
        pass

    def __getattr__(self, name):
        pass


class ClientContext(BaseClient, ContextManager):
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
