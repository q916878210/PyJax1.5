__author__ = 'Sean Mead'

__receivers = []


def register(rec):
    __receivers.append(rec)


def send(msg):
    for r in __receivers:
        r(msg)
