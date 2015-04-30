__author__ = 'Sean Mead'

from jax.core.modules import Session
from SqlDatabase import TableScheme, SqlDb
from types import FunctionType


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


class PerfectDecorator(object):
    @classmethod
    def on_call(cls, self, func, *args, **kwargs):
        return func()

    class InnerWrap(object):
        def __init__(self, on_call, *d_args, **d_kwargs):
            self.on_call = on_call
            self.__args = d_args
            self.__kwargs = d_kwargs

        def __call__(self, func):
            def inner_func_wrapper(_self=None, *f_args, **f_kwargs):
                if _self:
                    def inner_dec_wrap():
                        return func(_self, *f_args, **f_kwargs)
                    return self.on_call(_self, inner_dec_wrap, *self.__args, **self.__kwargs)
                else:
                    def inner_dec_wrap():
                        return func(*f_args, **f_kwargs)
                    return self.on_call(_self, inner_dec_wrap, *self.__args, **self.__kwargs)
            return inner_func_wrapper

    @classmethod
    def decorate(cls, *args, **kwargs):
        if args and type(args[0]) == FunctionType:
            return PerfectDecorator.InnerWrap(cls.on_call).__call__(args[0])
        else:
            return PerfectDecorator.InnerWrap(cls.on_call, *args, **kwargs)


class IsPost(PerfectDecorator):
    @classmethod
    def on_call(cls, self, func, negate=False, on_fail=None):
        p = self.handler.POST
        if negate:
            p = not p
        if p:
            return func()
        elif on_fail:
            self.handler.sync_path(on_fail)
            if on_fail in dir(self):
                return getattr(self, on_fail)()


class IsGet(PerfectDecorator):
    @classmethod
    def on_call(cls, self, func, negate=False, on_fail=None):
        g = self.handler.GET
        if negate:
            g = not g
        if g:
            return func()
        elif on_fail:
            self.handler.sync_path(on_fail)
            if on_fail in dir(self):
                return getattr(self, on_fail)()


class IsValid(PerfectDecorator):
    @classmethod
    def on_call(cls, self, func, negate=False, on_fail=None):
        v = Session.valid(self.handler)
        if negate:
            v = not v
        if v:
            return func()
        elif on_fail:
            self.handler.sync_path(on_fail)
            if on_fail in dir(self):
                return getattr(self, on_fail)()


def p_decorate(func):
    def func_wrapper(*args, **kwargs):
        return "<p>{0}</p>".format(func(*args, **kwargs))
    return func_wrapper
