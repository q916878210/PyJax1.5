"""
Created on Oct 1, 2014

@author: Sean Mead
"""

import socket
from threading import Thread
from jax.core.modules.Settings import Config


socket_clients = {}


def add(username, connection):
    conns = [connection, ]
    if username in socket_clients:
        conns += socket_clients.get(username)
    socket_clients.update({username: conns})


def send_command(username, cid, call, text):
    cid = '"cid":"%s"' % cid
    call = '"call":"%s"' % call
    text = '"response":%s' % text if text.startswith('[') and text.endswith(']') else '"response":"%s"' % text
    send(username, '{%s, %s, %s}' % (cid, call, text))


def send(username, code=''):
    if username in socket_clients:
        handlers = socket_clients.pop(username)
        for handler in handlers:
            try:
                handler.send(code)
            except Exception:
                handler.close()
                handlers.remove(handler)
        if len(handlers) != 0:
            socket_clients[username] = handlers


class SocketUpdateHandler(Thread):
    def __init__(self, *args):
        Thread.__init__(self)
        self.daemon = True
        self.__connection, self.__address = args

    def __receive_line(self):
        line = ''
        char = ''
        while char != '\n':
            char = self.__connection.recv(1)
            line += char
        return line[:-1]

    def __send_line(self, text):
        self.__connection.send(text + '\n')

    def __transaction(self, call, arg=None):
        self.__send_line('{"call":"%s", "arg": "%s"}' % (call, arg))
        return self.__receive_line()

    def run(self):
        self.__receive_line()
        account = self.__transaction('prompt', 'Account: ')
        if account in socket_clients:
            cid = self.__transaction('prompt', 'CID: ')
            call = self.__transaction('prompt', 'Call: ')
            text = self.__transaction('prompt', 'Text: ')
            send_command(account, cid, call, text)
        status = self.__transaction('quit')


class SocketUpdateThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.__running = False
        self.__port = Config.get_server()['socket_update_port']
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__name = 'Update Server'

    @staticmethod
    def new():
        return SocketUpdateThread()

    @property
    def name(self):
        return self.__name

    @property
    def running(self):
        return self.__running

    @running.setter
    def running(self, running):
        self.__running = running

    def run(self):
        self.__running = True
        try:
            self.__server.bind(('localhost', self.__port))
            self.__server.listen(1)
        except Exception as e:
            print e
            self.__running = False
        while self.__running:
            try:
                SocketUpdateHandler(*self.__server.accept()).start()
            except Exception as e:
                print e