"""
Created on Oct 1, 2014

@author: Sean Mead
"""

import os
from inspect import trace
import uuid
import time
import socket
import ssl
import xmlrpclib
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from SocketServer import ThreadingMixIn
from threading import Thread

from jax.core.modules.Coder import strip_item, get_item
from jax.core.modules.Tools import split_extension, human_gmt_time, File
from jax.core.modules.Event import Event
from jax.core.modules.Log import Log
from jax.core.modules.Settings import Config
from jax.core.modules.Builder import Static
from jax.core.modules.Media import TYPES
from jax.core.server.Client import Client
from jax.core.server.Attributes import Attributes


TMP_IGNORE_PATH = '/RPC2' + str(uuid.uuid4())


class ClientHandler(BaseHTTPRequestHandler):
    MAX_FILE_READ = 100000000

    def __init__(self, request, client_address, data):
        """
        Handler for the requests from the Server
        :param request:
        :param client_address:
        :param data:
        """
        BaseHTTPRequestHandler.__init__(self, request, client_address, data)
        self.__attributes = Attributes()
        self.__kwargs = {}
        self.__tmp = None
        self.__cookies = {}
        self.__header_count = 0
        self.__headers_send = []
        self.__headers_sent = False
        self.script_sync = ''

    def set_kwargs(self, **kwargs):
        if kwargs:
            self.__kwargs = kwargs

    def sync_path(self, path):
        if path.startswith('/'):
            path = path[1:]
        self.attributes.path = path.replace('_', '/').lower()
        self.script_sync = Static.Builder.sync_path(self.attributes.path)

    @property
    def kwargs(self):
        return self.__kwargs

    @property
    def tmp(self):
        """
        The tmp file location if triggered from file upload
        :return: The name of the tmp file.
        """
        return self.__tmp

    @property
    def attributes(self):
        """
        The req object containing the request information.
        :rtype : Req
        :return: req
        """
        return self.__attributes

    @attributes.setter
    def attributes(self, attributes):
        self.__attributes = attributes

    @property
    def GET(self):
        return self.__attributes.method == 'GET'

    @property
    def POST(self):
        return self.__attributes.method == 'POST'

    def address_string(self):
        """
        Override the built in address_string() to return the address.
        """
        return '%s:%s' % self.client_address

    def do_GET(self):
        """
        Called when a get request is triggered.
        Receives arguments, and triggers Client() get.
        """
        self.__receive()
        self.__attributes.method = "GET"
        Client(self).get()

    def do_POST(self):
        """
        Called when a post request is triggered.
        Receives arguments, checks content length and triggers Client() post.
        """
        if self.path != TMP_IGNORE_PATH:
            self.__receive()
            self.__attributes.method = "POST"
            length = long(self.headers.getheader('content-length'))
            line, index = self.__receive_line(length)
            if index < length:
                self.__read_file(line, length - index)
            self.__read_arguments(line)
        Client(self).post()

    def __read_file(self, line, length):
        """
        Reads the file that is uploaded into a temp directory.
        :param line: First line of the file
        :param length:  Length of the content
        """
        key = str(uuid.uuid4())
        self.__tmp = Config.TMP_DIR + str(key)

        with open(self.__tmp, 'wb') as o:
            o.write(line)
            loop = length / ClientHandler.MAX_FILE_READ
            m = length % ClientHandler.MAX_FILE_READ
            for i in range(0, loop):
                o.write(self.rfile.read(ClientHandler.MAX_FILE_READ))
            o.write(self.rfile.read(m))
        Event.add_event(obj=File(self.__tmp), method='delete', interval=4, onetime=True, key=key, start=True)

    def delete_tmp(self):
        """
        Delete the tmp file
        :return:
        """
        if self.__tmp:
            os.remove(self.__tmp)

    def move_tmp(self, path, fail=False):
        """
        Moves the tmp file to the specified path.
        :param path: directory to move the tmp file to
        :return: name of the file
        """
        if self.__tmp:
            Event.remove_event(key=self.__tmp)
            h = open(self.__tmp, 'rb')
            boundary = h.readline()
            filename = os.path.basename(get_item(h.readline(), 'filename')[1:-1])
            content_type = h.readline().split(': ')[-1]
            blank_line = h.readline()
            if not filename or filename == '':
                return
            if os.path.exists(path + filename):
                if fail:
                    return
                name, ext = split_extension(filename)
                filename = name + str(uuid.uuid4()) + '.' + ext
            with open(path + filename, 'wb') as o:
                o.writelines(h.readlines()[:-1])
            h.close()
            os.remove(self.__tmp)
            return filename

    def write_content(self, content):
        self.wfile.write(content)

    def write_headers(self, status='HTTP/1.0 200 OK'):
        if not self.__headers_sent:
            if self.__header_count == 0:
                self.set_header('Content-Type', 'text/html')
            self.connection.send('%s\r\n%s\r\n%s\r\n' % (status, 'Date: %s' % human_gmt_time(), ''.join(self.__headers_send)))
            self.__headers_sent = True
            return True

    def write(self, content):
        """
        Sends the content to the client with headers.
        :param content: Content to send
        """
        if self.write_headers():
            self.write_content(content)
        self.connection.shutdown(0)

    def set_cookie(self, name, value, expire_epoch):
        """
        Add cookie header with the name, value.
        :param name: Name of the cookie
        :param value: Value of the cookie
        """
        self.set_header('Set-Cookie', '%s=%s; Expires=%s' %
                        (name, value, time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.gmtime(expire_epoch))))

    def enable_build(self):
        self.__attributes.build = 'ajax' not in self.__attributes.arguments

    def set_content(self, value):
        if value in TYPES:
            value = '%s/%s' % (TYPES.get(value), value)
            self.__attributes.build = False
        self.set_header('Content-Type', value)

    def set_header(self, name, value):
        """
        Add a header with name, value
        :param name: Name of the header
        :param value: Value of the header
        """
        self.__header_count += 1
        self.__headers_send.append('%s: %s\r\n' % (name, value))

    def get_argument(self, name):
        """
        Convenience method to access handler arguments.
        :param name: Name of the argument
        :return: Value of the argument
        """
        return self.__attributes.arguments.get(name)

    def get_cookie(self, name):
        """
        Get the value of a cookie
        :param name: Name of the cookie to get
        :rtype : string
        """
        return self.__cookies.get(name)

    def __read_cookies(self):
        """
        Read in the cookies for the constructed headers.
        """
        cookies = self.headers.getheader('cookie')
        if cookies:
            cookies = cookies.split(';')
            for cookie in cookies:
                try:
                    name, value = cookie.strip().split('=', 2)
                    self.__cookies.update({name: value})
                except ValueError:
                    pass

    def __read_arguments(self, line):
        """
        Read arguments for the current line.
        """
        args = line.split('&')
        for arg in args:
            if '=' in arg:
                name, value = arg.split('=')
                self.__attributes.arguments.update({strip_item(name.strip()): strip_item(value.strip())})

    def __receive_line(self, length):
        """
        Receive a single line from the client.
        :return: The entire line, index of line.
        """
        line = ''
        char = ''
        index = 0
        while char != '\n' and index < length:
            char = self.rfile.read(1)
            line += char
            index += 1
        return line, index

    def __receive(self):
        """
        Do all receive
        """
        self.script_sync = ''
        self.__headers_sent = False
        self.__kwargs = {}
        self.__attributes = Attributes()
        self.__tmp = None
        self.__cookies = {}
        self.__header_count = 0
        self.__headers_send = []
        path = self.path.split('?')
        self.__attributes.path = path[0]
        if len(path) == 2:
            self.__read_arguments(path[1])
        self.__read_cookies()


class WebServer(ThreadingMixIn, HTTPServer):
    def __init__(self, args, handler):
        """
        Overrides the BaseHTTPServer to respond cleaner.
        :param args:
        :param handler:
        """
        HTTPServer.__init__(self, args, handler)
        self.daemon_threads = True
        self.__alive = False

    def alive(self):
        return self.__alive

    def power(self, value):
        self.__alive = value
        if value:
            self.serve_forever(0)
        else:
            self.server_close()

    def handle_error(self, request, address):
        Log.report_socket_error(address=address, traceback=trace()[-1][1:])

    def serve_forever(self, poll_interval=1):
        while self.__alive:
            self._handle_request_noblock()


class WebServerThread(Thread):
    def __init__(self, url):
        """
        Server object is used to host the normal WebServer.  No parameters are needed.
        """
        Thread.__init__(self)
        self.daemon = True
        self.__url = url
        _server = Config.get_server()
        self.__server = WebServer((_server['address'], _server['web_port']), ClientHandler)
        self.__server.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__server.allow_reuse_address = socket.SO_REUSEADDR
        cert = _server['cert']
        key = _server['key']
        if cert and key:
            self.__server.socket = ssl.wrap_socket(self.__server.socket, certfile=cert, keyfile=key, server_side=True)
        self.__name = 'Web Server'

    def new(self):
        self.__server.socket.close()
        return WebServerThread(self.__url)

    @property
    def name(self):
        return self.__name

    def spoof_request(self):
        try:
            server = xmlrpclib.Server(self.__url + TMP_IGNORE_PATH)
            server.ping()
        except Exception:
            pass

    @property
    def running(self):
        return self.__server.alive()

    @running.setter
    def running(self, running):
        self.__server.power(running)
        if not running:
            self.spoof_request()

    def run(self):
        self.__server.power(True)