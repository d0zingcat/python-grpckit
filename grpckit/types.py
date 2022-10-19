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
    def __init__(self):
        pass

    @property
    def proto(self):
        pass
