__author__ = 'Sean Mead'

from jax.core.modules import Session
from SqlDatabase import TableScheme, SqlDb


class Database(object):
    def __init__(self, obj):
        self.__obj = obj

    def __call__(self, *args, **kwargs):
        if isinstance(self.__obj, str):
            def func_wrapper(*o_args, **o_kwargs):
                return Database.__make(args[0], self.__obj, *o_args, **o_kwargs)
            return func_wrapper
        return Database.__make(self.__obj, None, *args, **kwargs)

    @staticmethod
    def __make(cls, root, *args, **kwargs):
        obj = cls(*args, **kwargs)
        obj.database = SqlDb(TableScheme(obj.__class__, obj.__dict__, root))
        obj.connect = obj.database.connect
        obj.query = obj.database.query
        return obj


class IsPost(object):
    def __init__(self, on_fail=None):
        self.on_fail = on_fail

    def __call__(self, func):
        def func_wrapper(_self):
            if _self.handler.POST:
                return func(_self)
            elif self.on_fail:
                _self.handler.sync_path(self.on_fail)
                if self.on_fail in dir(_self):
                    return getattr(_self, self.on_fail)()
        return func_wrapper


class IsGet(object):
    def __init__(self, on_fail=None):
        self.on_fail = on_fail

    def __call__(self, func):
        def func_wrapper(_self):
            if _self.handler.GET:
                return func(_self)
            elif self.on_fail:
                _self.handler.sync_path(self.on_fail)
                if self.on_fail in dir(_self):
                    return getattr(_self, self.on_fail)()
        return func_wrapper


def is_valid(func):
    def func_wrapper(self):
        if Session.valid(self.handler):
            return func(self)
    return func_wrapper


def p_decorate(func):
    def func_wrapper(*args, **kwargs):
        return "<p>{0}</p>".format(func(*args, **kwargs))
    return func_wrapper
