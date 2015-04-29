__author__ = 'seanmead'


class Callback(type):

    class Switch(object):
        def __init__(self, items):
            self.__items = items

        def switch(self, key, *args):
            if key in self.__items:
                if self.__items[key]:
                    return self.__items[key](*args)

    @staticmethod
    def as_switch(**kwargs):
        return Callback.Switch(kwargs)
