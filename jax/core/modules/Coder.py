"""
Created on Jan 30, 2014

@author: Sean Mead
"""

from urllib import unquote
import struct
import re


entity = {'&#8221': '"', '&#8220': '"', '&#8217;': "'", '&quot;': '"', '&#39;': "'", "&ldquo;": '"',
          "&rdquo;": '"'}


def decode(text):
    """
    Parse and decode a unicode String.
    """
    text = text.encode('ascii', 'ignore')
    for key, value in entity.items():
        text = text.replace(key, value)
    return text


def decode_socket(stream):
    """
    Decode a WebSocket.
    :param stream: Read in socket stream
    :return: Decoded stream
    """
    byte_array = [ord(character) for character in stream]
    data_length = byte_array[1] & 127
    index_first_mask = 2
    if data_length == 126:
        index_first_mask = 4
    elif data_length == 127:
        index_first_mask = 10
    masks = [m for m in byte_array[index_first_mask: index_first_mask + 4]]
    index_first_data_byte = index_first_mask + 4
    decoded_chars = []
    i = index_first_data_byte
    j = 0
    while i < len(byte_array):
        decoded_chars.append(chr(byte_array[i] ^ masks[j % 4]))
        i += 1
        j += 1
    return ''.join(decoded_chars)


def encode_socket(s):
        """
        WebSocket encode a string.
        :param s: String to encode
        :return: Encoded string.
        """
        message = ""
        b1 = 0x80
        payload = None
        if type(s) == unicode:
            b1 |= 0x01
            payload = s.encode("UTF8")
        elif type(s) == str:
            b1 |= 0x02
            payload = s

        message += chr(b1)

        b2 = 0
        length = len(payload)
        if length < 126:
            b2 |= length
            message += chr(b2)
        elif length < (2 ** 16) - 1:
            b2 |= 126
            message += chr(b2)
            l = struct.pack(">H", length)
            message += l
        else:
            l = struct.pack(">Q", length)
            b2 |= 127
            message += chr(b2)
            message += l

        message += payload

        return message


def get_item(data, item):
    """
    Get a data item specified by the Html Get format.
    :param data: full string
    :param item: item to find
    """
    op = data[data.index(item):]
    op = op.split('\n')[0].split('=')[1].split('&')[0]
    return strip_item(op)


def strip_item(item):
    """
    Decode a url string.
    :param item: String to strip
    """
    return unquote(item).decode('utf8').replace('+', ' ').replace('../', '').replace('./', '').strip()
