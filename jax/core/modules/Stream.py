__author__ = 'seanmead'

import os
from time import sleep, time
from jax.core.modules.Builder import Static, Header
from jax.core.modules.Settings import split_extension
from jax.core.modules.Media import TYPES
from jax.core.modules.Tools import get_files
from jax.core.modules.Log import Log


class StreamBlock(type):
    """
    Some browsers insist on spamming stream requests (I'm talking to you Safari)
    """
    ABUSE = 12
    TIMEOUT = 2
    penalty = {}

    @staticmethod
    def check(address):
        now = int(time())
        if address not in StreamBlock.penalty:
            StreamBlock.penalty[address] = [1, now]
            return False
        elif StreamBlock.penalty[address][0] < StreamBlock.ABUSE:
            StreamBlock.penalty[address][0] += 1
            return False
        elif (StreamBlock.penalty[address][1] + StreamBlock.TIMEOUT) < now:
            del StreamBlock.penalty[address]
            return False
        return True


class StreamFunction(type):
    @staticmethod
    def force_media(media, path):
        media = media.replace('/', '')
        name, ext = split_extension(media)
        header = Header('Content-Type', '%s/%s' % (TYPES.get(ext), ext))
        filename = os.path.join(path, media)
        return header, filename

    @staticmethod
    def get_file(filename, path):
        if path:
            if filename not in get_files(path):
                Log.report_error('No file found %s' % path)
                return None, None
            header, filename = StreamFunction.force_media(filename, path)
        else:
            header, filename = Static.Builder.find_media(filename)
        return header, filename

    @staticmethod
    def read_media(content_writer, filename, start, stop, length, check):
        stop += length - (stop - start)
        max_read = min(2000000, (stop-start) / 10)
        loop = (stop - start) / max_read
        m = (stop - start) % max_read

        with open(filename, 'rb') as o:
            o.seek(start)
            for i in range(0, loop):
                content_writer(o.read(max_read))
                #sleep(.01)
            content_writer(o.read(m))


class StreamHandler(object):
    def __init__(self, filename, path):
        self.__filename = filename
        self.__header, self.__path = StreamFunction.get_file(filename, path)

    def handle(self, handler):
        if not self.__path:
            return
        byte_range = handler.headers.getheader('range')
        length = os.path.getsize(self.__path)
        start = 0
        stop = length - 1
        response = 'HTTP/1.1 206 Partial Content'
        if not byte_range or '-' not in byte_range:
            handler.set_header(name='Content-Length', value=length)
        elif ',' in byte_range:
            handler.set_header(name='Content-Range', value='bytes %s-%s/%s' % (start, stop, length))
            response = 'HTTP/1.1 416 Requested Range Not Satisfiable'
        else:
            byte_range = byte_range.split('=', 1)[-1]
            r_start, r_stop = byte_range.split('-', 1)
            if not r_stop:
                r_stop = stop
            start = int(r_start)
            stop = int(r_stop)
            handler.set_header(name=self.__header.name, value=self.__header.value)
            handler.set_header(name='Content-Length', value=(stop - start + 1))
            handler.set_header(name='Content-Range', value='bytes %s-%s/%s' % (start, stop, length))

        handler.write_headers(response + '\r\n' + 'Accept-Ranges: 0-%s' % (length - 1))
        address = handler.address_string().split(':')[0]
        check = StreamBlock.check(address)
        if check:
            sleep(0.5)
        StreamFunction.read_media(handler.write_content, self.__path, start, stop, length, check)


def handle(handler, filename, path=None):
    StreamHandler(filename, path).handle(handler)