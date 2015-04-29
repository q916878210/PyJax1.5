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


class Mini(type):
    CSS_P = re.compile(
        r'([^\\"\047u>@\r\n\f\040\t/;:{}]+)|(?<=[{}(=:>+[,!])((?:[\r\n\f\040'
        r'\t]|(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*/))+)|^((?:[\r\n\f\040\t]|(?:/'
        r'\*[^*]*\*+(?:[^/*][^*]*\*+)*/))+)|((?:[\r\n\f\040\t]|(?:/\*[^*]*\*'
        r'+(?:[^/*][^*]*\*+)*/))+)(?=(([:{});=>+\],!])|$)?)|;((?:[\r\n\f\040'
        r'\t]|(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*/))*(?:;(?:[\r\n\f\040\t]|(?:/'
        r'\*[^*]*\*+(?:[^/*][^*]*\*+)*/))*)*)(?=(\})?)|(\{)|(\})|((?:(?:\047'
        r'[^\047\\\r\n\f]*(?:\\[^\r\n\f][^\047\\\r\n\f]*)*\047)|(?:"[^"\\\r\n'
        r'\f]*(?:\\[^\r\n\f][^"\\\r\n\f]*)*")))|(?<![^\000-\054\056\057\072-'
        r'\100\133-\136\140\173-\177])url\([\r\n\f\040\t]*((?:(?:\047[^\047'
        r'\\]*(?:\\(?:[^\r]|\r\n?)[^\047\\]*)*\047)|(?:"[^"\\]*(?:\\(?:[^\r]'
        r'|\r\n?)[^"\\]*)*"))|(?:(?:[^\000-\040"\047()\\\177]*(?:(?:\\(?:[0-'
        r'9a-fA-F]{1,6}(?:[\040\n\t\f]|\r\n?)?|[^\n\r\f0-9a-fA-F]))[^\000-\0'
        r'40"\047()\\\177]*)*)(?:(?:[\r\n\f\040\t]+|(?:\\(?:[\n\f]|\r\n?))+)'
        r'(?:(?:[^\000-\040"\047()\\\177]|(?:\\(?:[0-9a-fA-F]{1,6}(?:[\040\n'
        r'\t\f]|\r\n?)?|[^\n\r\f0-9a-fA-F]))|(?:\\(?:[\n\f]|\r\n?)))[^\000-'
        r'\040"\047()\\\177]*(?:(?:\\(?:[0-9a-fA-F]{1,6}(?:[\040\n\t\f]|\r\n'
        r'?)?|[^\n\r\f0-9a-fA-F]))[^\000-\040"\047()\\\177]*)*)+)*))[\r\n\f'
        r'\040\t]*\)|(@(?:[mM][eE][dD][iI][aA]|[sS][uU][pP][pP][oO][rR][tT]['
        r'sS]|[dD][oO][cC][uU][mM][eE][nN][tT]|(?:-(?:[wW][eE][bB][kK][iI][t'
        r'T]|[mM][oO][zZ]|[oO]|[mM][sS])-)?[kK][eE][yY][fF][rR][aA][mM][eE]['
        r'sS]))(?![^\000-\054\056\057\072-\100\133-\136\140\173-\177])|((?:>'
        r'/\*\*/))((?:[\r\n\f\040\t]|(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*/))*)|('
        r':[fF][iI][rR][sS][tT]-[lL](?:[iI][nN][eE]|[eE][tT][tT][eE][rR]))(('
        r'?:[\r\n\f\040\t]|(?:/\*[^*]*\*+(?:[^/*][^*]*\*+)*/))*)(?=[{,])|((?'
        r':(?:\047[^\047\\\r\n\f]*(?:\\(?:[^\r]|\r\n?)[^\047\\\r\n\f]*)*\047'
        r')|(?:"[^"\\\r\n\f]*(?:\\(?:[^\r]|\r\n?)[^"\\\r\n\f]*)*")))|((?:\\('
        r'?:[0-9a-fA-F]{1,6}(?:[\040\n\t\f]|\r\n?)?|[^\n\r\f0-9a-fA-F]))[^'
        r'\\"\047u>@\r\n\f\040\t/;:{}]*)')

    JS_P = re.compile(
        r'([^\047"/\000-\040]+)|((?:(?:\047[^\047\\\r\n]*(?:\\(?:[^\r\n]'
        r'|\r?\n|\r)[^\047\\\r\n]*)*\047)|(?:"[^"\\\r\n]*(?:\\(?:[^\r\n]'
        r'|\r?\n|\r)[^"\\\r\n]*)*"))[^\047"/\000-\040]*)|((?:/\*![^*]*\*'
        r'+(?:[^/*][^*]*\*+)*/)[^\047"/\000-\040]*)|(?<=[(,=:\[!&|?{};\r'
        r'\n])(?:[\000-\011\013\014\016-\040]|(?:/\*(?!!)[^*]*\*+(?:[^/*'
        r'][^*]*\*+)*/))*(?:(?:(?://[^\r\n]*)?[\r\n])(?:[\000-\011\013\0'
        r'14\016-\040]|(?:/\*(?!!)[^*]*\*+(?:[^/*][^*]*\*+)*/))*)*((?:/('
        r'?![\r\n/*])[^/\\\[\r\n]*(?:(?:\\[^\r\n]|(?:\[[^\\\]\r\n]*(?:'
        r'\\[^\r\n][^\\\]\r\n]*)*\]))[^/\\\[\r\n]*)*/)[^\047"/\000-\040]'
        r'*)|(?<=[\000-#%-,./:-@\[-^`{-~-]return)(?:[\000-\011\013\014\0'
        r'16-\040]|(?:/\*(?!!)[^*]*\*+(?:[^/*][^*]*\*+)*/))*(?:(?:(?://['
        r'^\r\n]*)?[\r\n])(?:[\000-\011\013\014\016-\040]|(?:/\*(?!!)[^*'
        r']*\*+(?:[^/*][^*]*\*+)*/)))*((?:/(?![\r\n/*])[^/\\\[\r\n]*(?:('
        r'?:\\[^\r\n]|(?:\[[^\\\]\r\n]*(?:\\[^\r\n][^\\\]\r\n]*)*\]))[^/'
        r'\\\[\r\n]*)*/)[^\047"/\000-\040]*)|(?<=[^\000-!#%&(*,./:-@\[\\'
        r'^`{|~])(?:[\000-\011\013\014\016-\040]|(?:/\*(?!!)[^*]*\*+(?:['
        r'^/*][^*]*\*+)*/))*(?:((?:(?://[^\r\n]*)?[\r\n]))(?:[\000-\011'
        r'\013\014\016-\040]|(?:/\*(?!!)[^*]*\*+(?:[^/*][^*]*\*+)*/))*)+'
        r'(?=[^\000-\040"#%-\047)*,./:-@\\-^`|-~])|(?<=[^\000-#%-,./:-@'
        r'\[-^`{-~-])((?:[\000-\011\013\014\016-\040]|(?:/\*(?!!)[^*]*\*'
        r'+(?:[^/*][^*]*\*+)*/)))+(?=[^\000-#%-,./:-@\[-^`{-~-])|(?<=\+)'
        r'((?:[\000-\011\013\014\016-\040]|(?:/\*(?!!)[^*]*\*+(?:[^/*][^'
        r'*]*\*+)*/)))+(?=\+)|(?<=-)((?:[\000-\011\013\014\016-\040]|(?:'
        r'/\*(?!!)[^*]*\*+(?:[^/*][^*]*\*+)*/)))+(?=-)|(?:[\000-\011\013'
        r'\014\016-\040]|(?:/\*(?!!)[^*]*\*+(?:[^/*][^*]*\*+)*/))+|(?:(?'
        r':(?://[^\r\n]*)?[\r\n])(?:[\000-\011\013\014\016-\040]|(?:/\*('
        r'?!!)[^*]*\*+(?:[^/*][^*]*\*+)*/))*)+')

    @staticmethod
    def js(text):
        groups = []
        for item in Mini.JS_P.finditer(text):
            groups += [group for group in item.groups() if group]
        return ''.join(groups)

    @staticmethod
    def css(text):
        p = ''
        # url() doesn't need quotes
        text = re.sub(r'url\((["\'])([^)]*)\1\)', r'url(\2)', text)

        # spaces may be safely collapsed as generated content will collapse them anyway
        text = re.sub(r'\s+', ' ', text)

        # shorten collapsable colors: #aabbcc to #abc
        text = re.sub(r'#([0-9a-f])\1([0-9a-f])\2([0-9a-f])\3(\s|;)', r'#\1\2\3\4', text)

        # fragment values can loose zeros
        text = re.sub(r':\s*0(\.\d+([cm]m|e[mx]|in|p[ctx]))\s*;', r':\1;', text)

        for rule in re.findall(r'([^{]+){([^}]*)}', text):

            # we don't need spaces around operators
            selectors = [re.sub(r'(?<=[\[\(>+=])\s+|\s+(?=[=~^$*|>+\]\)])', r'', selector.strip()) for selector in rule[0].split( ',' )]

            # order is important, but we still want to discard repetitions
            properties = {}
            porder = []
            for prop in re.findall('(.*?):(.*?)(;|$)', rule[1]):
                key = prop[0].strip().lower()
                if key not in porder: porder.append(key)
                properties[key] = prop[1].strip()

            # output rule if it contains any declarations
            if properties:
                p += "%s{%s}" % (','.join(selectors), ''.join(['%s:%s;' % (key, properties[key]) for key in porder])[:-1])
        return p
