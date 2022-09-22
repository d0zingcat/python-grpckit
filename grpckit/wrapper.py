from contextlib import contextmanager

import grpc

from grpckit.common import ContextManager


class GrpcKitClient(ContextManager):
    def __init__(self, target, credentials=None):
        self.secure = False
        if credentials:
            self.secure = True
        if len(target.split(":")) != 2:
            raise ValueError("Invalid target, should be like localhost:50051")
        self.target = target

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
