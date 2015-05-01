__author__ = 'Sean Mead'

from jax.core.modules import Broadcast
from jax.core.modules.Settings import Config, split_extension, read_file, LogPool
from jax.core.modules.Media import TYPES
from jax.core.modules.Parser import InjectParse, Mini


class Builder(object):
    def __init__(self):
        """
        Create a Builder object

        """
        self.__data = Config.get_data()
        self.__page_args = {}
        for page, args in self.__data['pages'].iteritems():
            i = InjectParse(args).inserts
            n_i = {}
            for key, value in i.iteritems():
                n_key = key.replace('kwargs:', '').strip().split('=')
                n_i[n_key[0]] = [n_key[-1], value]
            self.__page_args[page] = n_i

        self.__jax = self.__data['jax']
        if Config.get('mini'):
            self.__jax = Mini.js(self.__jax)

        self.__sync_path = '\n<script>\n%s\n</script>' % self.__data['sync_path']
        self.__frame_scripts = ('\n'.join(self.__data['frame_js'].values())).strip() \
            if len(self.__data['frame_js']) > 0 else ''
        if Config.get('mini'):
            self.__frame_scripts = Mini.js(self.__frame_scripts)
        self.__frame_scripts = '<script>\n%s\n</script>' % self.__frame_scripts if len(self.__frame_scripts) > 0 else ''

        self.__media = self.__data['media']
        self.__images = self.__data['img']
        self.__script = self.__data['js']
        self.__style = self.__data['style']
        self.__header = '\n<head>\n' + self.__data['head'] + self.__get_style_links() + \
                        ('\n<script>\n%s\n</script>\n' % self.__jax) + self.__frame_scripts + '\n</head>'
        self.__body = '\n<body>\n' + self.__data['nav'] + '\n' + self.__data['frame'] + self.__data['footer'] + \
                      self.__get_script_links() + '\n</body>'

    def __get_script_links(self):
        """
        Return the html formatted javascript.
        """
        if Config.get('mini'):
            for key, value in self.__script.iteritems():
                self.__script[key] = Mini.js(value)
        return '\n<script>\n%s\n</script>' % ('\n'.join(self.__script.values())).strip() \
            if len(self.__script) > 0 else ''

    def __get_style_links(self):
        """
        Return the html formatted stylesheet.
        :return:
        """
        if Config.get('mini'):
            for key, value in self.__style.iteritems():
                self.__style[key] = Mini.css(value)
        return '<style>\n%s\n</style>' % ('\n'.join(self.__style.values())).strip() if len(self.__style) > 0 else ''

    def sync_path(self, path):
        return self.__sync_path.replace(Config.KEY_PATH, path)

    def find_page(self, name, **kwargs):
        """
        Return the request html page if found.
        """
        name = name.replace('/', '').lower()
        if name in self.__data['pages']:
            data = self.__data['pages'][name]
            for key, value in self.__page_args[name].iteritems():
                if key in kwargs:
                    data = data.replace(value[1], kwargs[key])
                else:
                    data = data.replace(value[1], value[0])
            return data
        return False

    def find_media(self, media):
        media = media.replace('/', '')
        name, ext = split_extension(media)
        header = Header('Content-Type', '%s/%s' % (TYPES.get(ext), ext))
        f = None
        if media in self.__media:
            f = self.__media[media]
        return header, f

    def find_asset(self, asset):
        """
        Return a list containing the Header, and the Asset string.
        :param asset:
        :return:
        :rtype : list
        """
        asset = asset.replace('/', '')
        name, ext = split_extension(asset)
        if ext:
            if ext == 'js':
                return None, self.__script[asset]
            elif ext == 'css':
                return None, self.__style[asset]
            elif ext in TYPES:
                return self.__get_other_asset(asset, ext)
        else:
            if asset == 'jax':
                return Header('Content-Type', 'text/javascript'), self.__jax
        return Header.void(), self.__data['404']

    def __get_other_asset(self, asset, ext):
        """
        Return asset specifying the extension.
        :param asset:
        :param ext:
        :return:
        """
        header = Header('Content-Type', '%s/%s' % (TYPES.get(ext), ext))
        f = None
        if asset in self.__media:
            f = read_file(self.__media[asset])
        elif asset in self.__images:
            f = read_file(self.__images[asset])
        return header, f

    def get_document(self, content=None, script=None):
        """
        Return the entire html document with content injected
        :param content:
        :return:
        """
        page = "<!DOCTYPE html>\n<html>" + self.__header + self.__body
        if content:
            page = page.replace(Config.KEY_CONTENT_2, str(content).encode('ascii', errors='strict'))
        if script:
            page += script
        return page + "\n</html>"


class Header(object):
    def __init__(self, name, value):
        """
        Create a header object with name, value
        :param name:
        :param value:
        :rtype : Header
        """
        self.__name = name
        self.__value = value

    @property
    def name(self):
        return self.__name

    @property
    def value(self):
        """
        Return the value of the header.
        """
        return self.__value

    @staticmethod
    def basic():
        """
        Return a default text/html header.
        :rtype : Header
        """
        return Header('Content-Type', 'text/html')

    @staticmethod
    def void():
        """
        Return an empty header.
        :rtype : Header
        """
        return Header('', '')


class Static(type):
    Builder = Builder()

    @staticmethod
    def do_read(msg):
        Static.Builder = Builder()

Broadcast.register(Static.do_read)
