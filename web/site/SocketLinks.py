__author__ = 'seanmead'

from jax.core.modules import Session
from jax.core.server import SocketClients


class SocketLinks(object):
    def __init__(self, handler):
        """
        The socket object creates links used by the client's socket connection.
        :param handler: the handler of the client
        """
        self.__handler = handler

    def validate(self):
        """
        Validate appends the clients connection to the known connections list.
        :return:
        """
        if Session.valid(self.__handler):
            SocketClients.add(Session.get_name(self.__handler), self.__handler)
            return True
        return False
