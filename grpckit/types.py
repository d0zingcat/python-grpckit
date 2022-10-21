from google.protobuf.message import Message

from .utils.parser import MessageToDict


class WrappedDict(dict):
    def __getattr__(self, k):
        try:
            # parse KeyError to AttributeError, which enables hasattr works as a daisy.
            return self.__getitem__(k)
        except KeyError:
            raise AttributeError(k)

    def __setattr__(self, k, v):
        self.__setitem__(k, v)

    @classmethod
    def convert_from_dict(cls, dct: dict):
        ins = cls(**dct)
        for k, v in ins.items():
            if isinstance(v, dict):
                ins[k] = cls.convert_from_dict(v)
        return ins


class GrpcKitRequest:
    def __init__(self):
        pass


class GrpcKitResponse:
    RAW_DATA_TYPE_PROTO = "proto"
    RAW_DATA_TYPE_DICT = "dict"

    def load_data(self, data):
        self._raw_data = data
        if isinstance(data, Message):
            self._raw_data_type = self.RAW_DATA_TYPE_PROTO
            self._native_dict = MessageToDict(message=data)
        elif isinstance(data, dict):
            self._raw_data_type = self.RAW_DATA_TYPE_DICT
            self._native_dict = data
        else:
            raise ValueError("Invalid data type, should be protobuf message or python dict")
        self._wrapped_dict = WrappedDict(self._native_dict)

    def __init__(self, data=None):
        if data:
            self.load_data(data)
        self._ok = True
        self._msg = ""

    @property
    def proto(self):
        if self._raw_data_type == self.RAW_DATA_TYPE_PROTO:
            return self._raw_data
        raise ValueError("Raw data is not protobuf!")

    @property
    def msg(self):
        return self._msg

    @msg.setter
    def msg(self, msg):
        self._msg = msg

    @property
    def ok(self):
        return self._ok

    @ok.setter
    def ok(self, ok):
        self._ok = ok

    @property
    def data(self):
        return self._wrapped_dict

    @property
    def native_data(self):
        return self._native_dict
