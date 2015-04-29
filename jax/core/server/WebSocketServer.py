"""
Created on Jan 26, 2015

@author: Sean Mead
"""

from base64 import b64encode
from select import select
import socket
import hashlib
from ssl import wrap_socket
from threading import Thread

from jax.core.modules.Settings import Config
from jax.core.modules.Coder import strip_item
from jax.core.modules.Coder import encode_socket
from jax.core.server.Client import Client
from jax.core.server.Attributes import Attributes


KEY_SOCKET = '258EAFA5-E914-47DA-95CA-C5AB0DC85B11'


class SocketHandler(object):
    def __init__(self, connection):
        """
        Handler for requests from the WebSocketServer
        :param connection: Socket
        """
        self.daemon = True
        self.__connection = connection
        self.__connection.setblocking(0)
        self.__attributes = Attributes()
        self.__headers = {}
        self.__cookies = {}
        self.__header_count = 0
        self.__headers_send = []
        self.__headers_str = ''
        self.__handshake = False

    @property
    def connection(self):
        return self.__connection

    @property
    def attributes(self):
        return self.__attributes

    def ready(self):
        if self.__headers_str != '':
            return True
        headers = self.__connection.recv(2048)
        if headers != '':
            self.__headers_str = headers
            return True
        return False

    def send(self, content):
        self.__connection.send(encode_socket(content))

    def do_handle(self):
        if not self.__handshake:
            self.__receive()
            self.__complete_handshake()
        if not Client(self).socket():
            self.close()

    def __receive(self):
        self.__read_headers()
        path = self.attributes.path.split('?')
        self.attributes.path = path[0]
        if len(path) == 2:
            self.__read_arguments(path[1])
        self.__read_cookies()

    def __complete_handshake(self):
        self.__build_socket_headers()
        self.__connection.send('HTTP/1.1 101 Switching Protocols\r\n%s\r\n' % ''.join(self.__headers_send))
        self.__handshake = True

    def __finish_headers(self, attempts=12):
        while not self.__headers_str.endswith('\r\n\r\n') and attempts >= 0:
            self.__headers_str += self.__connection.recv(2048)
        return self.__headers_str.endswith('\r\n\r\n')

    def close(self):
        try:
            self.__connection.close()
        except Exception:
            pass

    def get_cookie(self, name):
        return self.__cookies.get(name)

    def set_cookie(self, name, value):
        self.set_header('Set-Cookie', '%s=%s; Expires=Wed, 09 Jun 2021 10:18:14 GMT' % (name, value))

    def get_argument(self, name):
        return self.attributes.arguments.get(name)

    def set_header(self, name, value):
        self.__header_count += 1
        self.__headers_send.append('%s: %s\r\n' % (name, value))

    def __read_headers(self):
        if not self.__headers_str.endswith('\r\n\r\n'):
            if not self.__finish_headers():
                return
        headers = self.__headers_str.split('\n')
        method, path, protocol = headers.pop(0).split(' ', 3)
        self.attributes.path = path
        for header in headers:
            if ':' in header:
                name, value = header.split(':', 1)
                self.__headers.update({name.strip(): value.strip()})

    def __read_cookies(self):
        if 'Cookie' in self.__headers:
            cookies = self.__headers.get('Cookie')
            if cookies:
                cookies = cookies.split(';')
                for cookie in cookies:
                    name, value = cookie.strip().split('=', 2)
                    self.__cookies.update({name: value})

    def __read_arguments(self, line):
        args = line.split('&')
        for arg in args:
            if '=' in arg:
                name, value = arg.split('=')
                self.attributes.arguments.update({strip_item(name.strip()): strip_item(value.strip())})

    def __build_socket_headers(self):
        self.set_header('Upgrade', self.__headers.get('Upgrade'))
        self.set_header('Connection', self.__headers.get('Connection'))
        self.set_header('Sec-WebSocket-Protocol', self.__headers.get('Sec-WebSocket-Protocol'))
        key = self.__headers.get('Sec-WebSocket-Key')
        if key:
            self.set_header('Sec-WebSocket-Accept', b64encode(hashlib.sha1(key + KEY_SOCKET).digest()))


class WebSocketThread(Thread):
    def __init__(self):
        """
        WebSocketServer object is used to host the SocketServer.  No parameters are needed.
        """
        Thread.__init__(self)
        self.daemon = True
        self.__ports = Config.get('server')
        self.__running = False
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__cert = Config.get('cert')
        self.__key = Config.get('key')
        if self.__key and self.__cert:
            self.__server = wrap_socket(self.__server, certfile=self.__cert, keyfile=self.__key, server_side=True)
        self.__listeners = [self.__server]
        self.__handlers = {}
        self.__name = 'Socket Server'

    @staticmethod
    def new():
        return WebSocketThread()

    @property
    def name(self):
        return self.__name

    def __open_connection(self):
        connection = None
        try:
            connection, address = self.__server.accept()
            file_no = connection.fileno()
            self.__listeners.append(file_no)
            self.__handlers[file_no] = SocketHandler(connection)
        except Exception as e:
            print 'bad connect: %s' % e
            if connection:
                connection.close()

    @property
    def running(self):
        return self.__running

    @running.setter
    def running(self, running):
        self.__running = running

    def run(self):
        self.__running = True
        try:
            self.__server.bind((self.__ports.get('address'), self.__ports.get('web_socket_port')))
            self.__server.listen(500)
        except Exception as e:
            print e
            self.__running = False
        while self.__running:
            ready_list, wait_list, dead_list = select(self.__listeners, [], self.__listeners, 1)
            for item in ready_list:
                if item == self.__server:
                    self.__open_connection()
                else:
                    handler = self.__handlers.get(item)
                    if handler.ready():
                        handler.do_handle()
                    del self.__handlers[item]
                    self.__listeners.remove(item)

            for item in dead_list:
                print item
                if item == self.__server:
                    self.__running = False
                else:
                    self.__handlers.get(item).close()
                    del self.__handlers[item]
                    self.__listeners.remove(item)