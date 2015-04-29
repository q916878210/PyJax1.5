__author__ = 'Sean Mead'

import time


observers = {}


def message(name, key):
    if name in observers:
        observers.get(name).message_received(key)


def register(name):
    o = Observer(name)
    observers.update({name: o})
    return o.wait_for_message()


class Observer(object):
    def __init__(self, name):
        self.__name = name
        self.__wait = True
        self.__key = None

    def wait_for_message(self):
        while self.__wait:
            time.sleep(1)
        return self.__key

    def message_received(self, key):
        self.__key = key
        self.__wait = False