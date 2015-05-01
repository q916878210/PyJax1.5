"""
Created on Jan 30, 2014

@author: Sean Mead
"""

import imp
from jax.core.modules import Broadcast
from jax.core.modules.Builder import Static
from web.site.Links import Links
from web.site.SocketLinks import SocketLinks


class Client(object):
    def __init__(self, handler):
        """
        Create a client object.  Requires the Server.Handler object.
        :param handler:
        """
        self.__handler = handler
        self.__links = Links(self.__handler)
        self.__out_headers = []
        self.__request = self.__handler.attributes.path[1:].replace('/', '_').lower()

    def socket(self):
        """
        Initiate the socket connection by injecting WebSocket connection scripts.
        """
        sock = SocketLinks(self.__handler)
        if self.__request in dir(sock):
            return getattr(sock, self.__request)()

    def _send_all(self, content):
        """
        Write all content including the given html content and headers.
        This sends the content to the User.
        :param content:
        """
        for header in self.__out_headers:
            if header:
                self.__handler.set_header(name=header.name, value=header.value)
        self.__handler.write(content)

    def __page_logic(self, request):
        if request in dir(self.__links) and not request.startswith('_'):
            content = getattr(self.__links, request)()
            if not content:
                content = Static.Builder.find_page(self.__handler.attributes.path, **self.__handler.kwargs)
        else:
            content = Static.Builder.find_page(self.__handler.attributes.path, **self.__handler.kwargs)
        return content

    def get(self):
        """
        Forward the get request through the content builders and asset handlers.
        """
        if self.__handler.attributes.path != '/':
            self.__handler.enable_build()
            content = self.__page_logic(self.__request)
            if content or content == "":
                if self.__handler.attributes.build:
                    script = None
                    if 'refresh_script' in dir(self.__links):
                        script = getattr(self.__links, 'refresh_script')()
                    content = Static.Builder.get_document(content=content, script=script)
            else:
                header, content = Static.Builder.find_asset(self.__handler.attributes.path)
                self.__out_headers.append(header)
        else:
            script = None
            if 'refresh_script' in dir(self.__links):
                script = getattr(self.__links, 'refresh_script')()
            content = Static.Builder.get_document(script=script)

        self._send_all(content + self.__handler.script_sync)

    def post(self):
        """
        Forward the post request through the content builders and asset handlers.
        """
        if self.__handler.attributes.path != '/':
            self._send_all(self.__page_logic(self.__request))


def do_load(msg):
    imp.reload(Links)
    imp.reload(SocketLinks)


Broadcast.register(do_load)
