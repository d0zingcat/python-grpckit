import copy
from threading import get_ident

""" Code stolen from werkzeug
"""


class Local:
    """ """

    __slots__ = ("__storage__", "__ident_func__")

    def __init__(self):
        object.__setattr__(self, "__storage__", {})
        object.__setattr__(self, "__ident_func__", get_ident)

    def __iter__(self):
        return iter(self.__storage__.items())

    def __call__(self, proxy):
        """ """
        return LocalProxy(self, proxy)

    def __release_local__(self):
        self.__storage__.pop(self.__ident_func__(), None)

    def __getattr__(self, name):
        try:
            return self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)  # pylint: disable=raise-missing-from

    def __setattr__(self, name, value):
        ident = self.__ident_func__()
        storage = self.__storage__
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}

    def __delattr__(self, name):
        try:
            del self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)  # pylint: disable=raise-missing-from


class LocalStack:
    """ """

    def __init__(self):
        self._local = Local()

    def __release_local__(self):
        self._local.__release_local__()

    @property
    def __ident_func(self):  # pylint: disable=unused-private-member
        return self._local.__ident_func__

    @__ident_func.setter
    def __ident_func__(self, value):
        object.__setattr__(self._local, "__ident_func__", value)

    def __call__(self):
        def _lookup():
            rv = self.top
            if rv is None:
                raise RuntimeError("Object unbond")
            return rv

        return LocalProxy(_lookup)

    def push(self, obj):
        """Push into stack"""
        rv = getattr(self._local, "stack", None)
        if rv is None:
            self._local.stack = rv = []  # pylint: disable=assigning-non-slot
        rv.append(obj)
        return rv

    def pop(self):
        stack = getattr(self._local, "stack", None)
        if stack is None:
            return None

        if len(stack) == 1:
            self._local.__release_local__()
            return stack[-1]

        return stack.pop()

    @property
    def top(self):
        """return stack top"""
        try:
            return self._local.stack[-1]
        except (AttributeError, IndexError):
            return None


class LocalProxy:
    """ """

    __slots__ = (
        "__local",
        "__dict__",
        "__name__",
        "__wrapped__",
    )  # pylint: disable=class-variable-slots-conflict

    def __init__(self, local, name=None):
        object.__setattr__(self, "_LocalProxy__local", local)
        object.__setattr__(self, "__name__", name)

        if callable(local) and not hasattr(local, "__release_local__"):
            object.__setattr__(self, "__wrapped__", local)

    def _get_current_object(self):
        """ """
        if not hasattr(self.__local, "__release_local__"):
            return self.__local()
        try:
            return getattr(self.__local, self.__name__)
        except AttributeError:
            raise RuntimeError(
                f"no object bond to {self.__name__}"
            )  # pylint: disable=(raise-missing-from

    @property
    def __dict__(self):
        try:
            return self._get_current_object().__dict__
        except RuntimeError:
            raise AttributeError("__dict__")  # pylint: disable=(raise-missing-from

    def __repr__(self):
        try:
            obj = self._get_current_object()
        except RuntimeError:
            return "<%s unbond>" % self.__class__.__name__
        return repr(obj)

    def __bool__(self):
        try:
            return bool(self._get_current_object())
        except RuntimeError:
            return False

    def __dir__(self):
        try:
            return dir(self._get_current_object())
        except RuntimeError:
            return []

    def __getattr__(self, name):
        if name == "__members__":
            return dir(self._get_current_object())
        return getattr(self._get_current_object(), name)

    def __setitem__(self, key, value):
        self._get_current_object()[key] = value

    def __delitem__(self, key):
        del self._get_current_object()[key]

    def __setattr__(x, n, v):
        return setattr(x._get_current_object(), n, v)

    def __delattr__(x, n):
        return delattr(x._get_current_object(), n)

    def __str__(x):
        return str(x._get_current_object())

    def __lt__(x, o):
        return x._get_current_object() < o

    def __le__(x, o):
        return x._get_current_object() <= o

    def __eq__(x, o):
        return x._get_current_object() == o

    def __ne__(x, o):
        return x._get_current_object() != o

    def __gt__(x, o):
        return x._get_current_object() > o

    def __ge__(x, o):
        return x._get_current_object() >= o

    def __hash__(x):
        return hash(x._get_current_object())

    def __call__(x, *a, **kw):
        return x._get_current_object()(*a, **kw)

    def __len__(x):
        return len(x._get_current_object())

    def __getitem__(x, i):
        return x._get_current_object()[i]

    def __iter__(x):
        return iter(x._get_current_object())

    def __contains__(x, i):
        return i in x._get_current_object()

    def __add__(x, o):
        return x._get_current_object() + o

    def __sub__(x, o):
        return x._get_current_object() - o

    def __mul__(x, o):
        return x._get_current_object() * o

    def __floordiv__(x, o):
        return x._get_current_object() // o

    def __mod__(x, o):
        return x._get_current_object() % o

    def __divmod__(x, o):
        return x._get_current_object().__divmod__(o)

    def __pow__(x, o):
        return x._get_current_object() ** o

    def __lshift__(x, o):
        return x._get_current_object() << o

    def __rshift__(x, o):
        return x._get_current_object() >> o

    def __and__(x, o):
        return x._get_current_object() & o

    def __xor__(x, o):
        return x._get_current_object() ^ o

    def __or__(x, o):
        return x._get_current_object() | o

    def __div__(x, o):
        return x._get_current_object().__div__(o)

    def __truediv__(x, o):
        return x._get_current_object().__truediv__(o)

    def __neg__(x):
        return -(x._get_current_object())

    def __pos__(x):
        return +(x._get_current_object())

    def __abs__(x):
        return abs(x._get_current_object())

    def __invert__(x):
        return ~(x._get_current_object())

    def __complex__(x):
        return complex(x._get_current_object())

    def __int__(x):
        return int(x._get_current_object())

    def __float__(x):
        return float(x._get_current_object())

    def __oct__(x):
        return oct(x._get_current_object())

    def __hex__(x):
        return hex(x._get_current_object())

    def __index__(x):
        return x._get_current_object().__index__()

    def __coerce__(x, o):
        return x._get_current_object().__coerce__(x, o)

    def __enter__(x):
        return x._get_current_object().__enter__()

    def __exit__(x, *a, **kw):
        return x._get_current_object().__exit__(*a, **kw)

    def __radd__(x, o):
        return o + x._get_current_object()

    def __rsub__(x, o):
        return o - x._get_current_object()

    def __rmul__(x, o):
        return o * x._get_current_object()

    def __rdiv__(x, o):
        return o / x._get_current_object()

    __rtruediv__ = __rdiv__

    def __rfloordiv__(x, o):
        return o // x._get_current_object()

    def __rmod__(x, o):
        return o % x._get_current_object()

    def __rdivmod__(x, o):
        return x._get_current_object().__rdivmod__(o)

    def __copy__(x):
        return copy.copy(x._get_current_object())

    def __deepcopy__(x, memo):
        return copy.deepcopy(x._get_current_object(), memo)
