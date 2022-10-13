from typing import Optional, Dict, List

import simplejson as json

from .constant import (
    K_GRPCKIT_SEND_MESSAGE_MAX_LENGHT,
    K_GRPCKIT_RECEIVE_MESSAGE_MAX_LENGHT,
    K_GRPCKIT_OPTIONS,
)


class Config(dict):
    def __init__(self, config: Optional[Dict] = None) -> None:
        super().__init__()
        if config and isinstance(config, dict):
            self.update(config)

    def from_object(self, obj: object) -> None:
        for key in dir(obj):
            if not key.isupper():
                continue
            self[key] = getattr(obj, key)

    def from_dict(self, kw: dict) -> None:
        for key, value in kw.items():
            if not key.isupper():
                continue
            self[key] = value

    def from_json(self, json_str: str, encoding: str = "utf-8") -> None:
        json_obj = json.loads(json_str, encoding=encoding)
        if not isinstance(json_obj, dict):
            raise TypeError("Top structure of json must be dict")
        self.from_dict(json_obj)

    def rpc_options(self) -> List:
        """
        https://github.com/grpc/grpc/blob/v1.37.x/include/grpc/impl/codegen/grpc_types.h
        """
        options = list()

        # Default message length is 5MB
        max_send_message_length = self.get(
            K_GRPCKIT_SEND_MESSAGE_MAX_LENGHT, 1024 * 1024 * 5
        )
        max_receive_message_length = self.get(
            K_GRPCKIT_RECEIVE_MESSAGE_MAX_LENGHT, 1024 * 1024 * 5
        )

        options.append(("grpc.max_send_message_length", max_send_message_length))
        options.append(("grpc.max_receive_message_length", max_receive_message_length))

        # Add other custom defined grpc options
        for option in self.get(K_GRPCKIT_OPTIONS, list()):
            if not isinstance(option, tuple):
                continue
            options.append(option)

        return options
