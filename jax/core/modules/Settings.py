"""
Created on Oct 1, 2014

@author: Sean Mead
"""

import os
import time
import json
from collections import OrderedDict
from jax.core.modules.Parser import HtmlInjectParse, HtmlParse
from jax.core.modules.Tools import get_address, get_address_local


def get_files(path, ext=''):
    return [f for f in os.listdir(path) if
            os.path.isfile(os.path.join(path, f)) and f.endswith(ext) and not f.startswith('.')]


def split_extension(filename):
    name, ext = os.path.splitext(filename)
    ext = ext.replace(".", "")
    return name, ext


def find_file(path, search):
    for f in os.listdir(path):
        if os.path.isfile(os.path.join(path, f)) and search in f:
            return read_file(path + f)


def read_file(path):
    with open(path, 'rb') as h:
        f = h.read()
    return f


class LogPool(type):
    msg, err, sock = [], [], []

    @staticmethod
    def add_msg(msg):
        LogPool.msg.append(msg)

    @staticmethod
    def add_err(err):
        LogPool.err.append(err)

    @staticmethod
    def add_sock(address, request):
        LogPool.sock.append((address, request))


class Config(type):
    WORKING_DIR = os.path.abspath(os.path.dirname(os.path.dirname(os.path.realpath(__file__))) + '/../../') + '/'
    CONFIG_DIR = WORKING_DIR + 'config/'
    FRAMEWORK_DIR = WORKING_DIR + 'framework/'
    SCRIPT_DIR = FRAMEWORK_DIR + 'scripts/'
    WEB_DIR = WORKING_DIR + 'web/'
    HTML_DIR = WEB_DIR + 'html/'
    ASSET_DIR = WEB_DIR + 'assets/'
    CERT_DIR = WORKING_DIR + 'certs/'
    DB_DIR = WORKING_DIR + 'database/'
    USER_DIR = WORKING_DIR + 'users/'
    CACHE_DIR = WORKING_DIR + 'cache/'
    TMP_DIR = WORKING_DIR + 'tmp/'

    VAR = str(time.time())

    TMP_VAR = 'tmp-' + VAR
    SERVER_VAR = 'server-' + VAR
    DATA_VAR = 'data-' + VAR
    CONFIG_VAR = 'config-' + VAR

    KEY_PATH = '{%!!path%}'
    KEY_CONTENT_1 = '{%!!content%}'
    KEY_CONTENT_2 = '<!--{%!!content%}-->'
    KEY_FRAME_ID = '{%!!frame_id%}'
    KEY_LINKS = '{%!!links%}'

    REQ_SCRIPTS = ['jax.js', 'sync_path.js']

    settings = None

    @staticmethod
    def load_dir(path):
        files = get_files(path)
        l_files = {}
        for item in files:
            l_files[item] = read_file(os.path.join(path, item))
        return l_files


    @staticmethod
    def get(item):
        if item in Config.settings[Config.CONFIG_VAR]:
            return Config.settings[Config.CONFIG_VAR][item]

    @staticmethod
    def get_data():
        return Config.settings[Config.DATA_VAR]

    @staticmethod
    def get_server():
        return Config.settings[Config.SERVER_VAR]

    @staticmethod
    def load_server(**kwargs):
        Config.settings[Config.SERVER_VAR].update(kwargs)

    @staticmethod
    def get_tmp(key):
        if key in Config.settings[Config.TMP_VAR]:
            return Config.settings[Config.TMP_VAR][key]

    @staticmethod
    def load_tmp(**kwargs):
        Config.settings[Config.TMP_VAR].update(kwargs)


class StaticSettings(type):
    class SettingsReader(object):
        def __init__(self):
            config = self._read_config()

            server = self._read_server()
            server.update(self._read_cert())

            data = self._read_head()
            t = HtmlParse(data['head']).find('title')
            if t:
                config['title'] = t.inner()
            else:
                config['title'] = 'No Title'

            data.update(self._read_jax())
            data.update(self._read_frame_scripts())
            data.update(self._read_frame(data))
            data.update(self._read_nav(self._read_links()))
            data.update(self._read_footer())
            data.update(self._read_html())
            data.update(self._read_style())
            data.update(self._read_images())
            data.update(self._read_javascript())
            data.update(self._read_media())
            data.update(self._read_404())

            self.__settings = self.__parse_all(config, server, data)

        @property
        def settings(self):
            return self.__settings

        def __parse_all(self, config, server, data):
            for sets in data:
                if isinstance(data[sets], dict):
                    for sub_set in data[sets]:
                        if isinstance(data[sets][sub_set], str):
                            data[sets][sub_set] = self.__process_parts(config, data[sets][sub_set])
                elif isinstance(data[sets], str):
                    data[sets] = self.__process_parts(config, data[sets])

            settings = {Config.TMP_VAR: {},
                        Config.CONFIG_VAR: config,
                        Config.SERVER_VAR: server,
                        Config.DATA_VAR: data}
            return settings

        @staticmethod
        def __process_parts(config, data):
            hip = HtmlInjectParse(data)
            for key, value in config.iteritems():
                if key in hip.inject.inserts:
                    data = data.replace(hip.inject.inserts[key], value)
            for trigger in hip.get_triggers():
                for node in trigger:
                    r = node.function()
                    data = data.replace(node.tag, str(r) if r else '', 1)
            return data

        @staticmethod
        def _read_config():
            configs = {}
            for key, value in dict(json.loads(read_file(Config.CONFIG_DIR + 'config.json'))).iteritems():
                key_new = key.lower() if isinstance(key, str) else key
                value_new = value.lower() if isinstance(value, str) else value
                configs.update({key_new: value_new})
            return configs

        @staticmethod
        def _read_server():
            server = {}
            for key, value in dict(json.loads(read_file(Config.CONFIG_DIR + 'server.json'))).iteritems():
                key_new = key.lower() if isinstance(key, str) else key
                value_new = value.lower() if isinstance(value, str) else value
                if key_new == 'address':
                    if value_new == 'auto':
                        value_new = get_address()
                        if not value_new:
                            value_new = 'localhost'
                            LogPool.add_err('Unable to determine ip: using localhost')
                    if value_new == 'localhost':
                        value_new = get_address_local()
                elif 'port' in key_new:
                    value_new = int(value_new)
                server.update({key_new: value_new})
            return server

        @staticmethod
        def _read_head():
            return {'head': str(read_file(Config.FRAMEWORK_DIR + 'head.html'))}

        @staticmethod
        def _read_jax():
            jax = read_file(Config.SCRIPT_DIR + Config.REQ_SCRIPTS[0])
            sync_path = read_file(Config.SCRIPT_DIR + Config.REQ_SCRIPTS[1])
            return {'jax': str(jax), 'sync_path': str(sync_path)}

        @staticmethod
        def _read_frame_scripts():
            files = get_files(Config.SCRIPT_DIR, 'js')
            javascript = {}
            for item in files:
                if item not in Config.REQ_SCRIPTS:
                    js = read_file(Config.SCRIPT_DIR + item)
                    javascript.update({item: str(js)})
            return {'frame_js': javascript}

        @staticmethod
        def _read_404():
            return {'404': str(read_file(Config.FRAMEWORK_DIR + '404.html'))}

        @staticmethod
        def _read_frame(data):
            frame = read_file(Config.FRAMEWORK_DIR + 'frame.html')
            ins = HtmlInjectParse(frame, k2=True).find_insert('!content')
            if ins:
                ip_id = ins.parent().get('id')
                if ip_id:
                    data['jax'] = data['jax'].replace(Config.KEY_FRAME_ID, ip_id)
            return {'frame': str(frame.replace(Config.KEY_CONTENT_1, Config.KEY_CONTENT_2))}

        @staticmethod
        def _read_nav(links):
            nav = read_file(Config.FRAMEWORK_DIR + 'nav.html')
            nav = nav.replace(Config.KEY_LINKS, links)
            return {'nav': str(nav)}

        @staticmethod
        def _read_links():
            links_html = ''
            link_options = ''
            links = dict(json.loads(read_file(Config.CONFIG_DIR + 'links.json'), object_pairs_hook=OrderedDict))
            if 'options' in links:
                link_options = links['options']
            if 'links' in links:
                for key, value in links['links'].iteritems():
                    links_html += '<li page="%s" %s ><label>%s</label></li>' % (value, link_options, key)
            return links_html

        @staticmethod
        def _read_footer():
            return {'footer': str(read_file(Config.FRAMEWORK_DIR + 'footer.html'))}

        @staticmethod
        def _read_html():
            files = get_files(Config.HTML_DIR, 'html')
            pages = {}
            for item in files:
                name, ext = split_extension(item)
                pages.update({name.lower(): str(read_file(Config.HTML_DIR + item))})
            return {'pages': pages}

        @staticmethod
        def _read_style():
            style = {}
            files = get_files(Config.ASSET_DIR + 'css/', 'css')
            for item in files:
                css = read_file(Config.ASSET_DIR + 'css/' + item)
                style.update({item: str(css)})
            return {'style': style}

        @staticmethod
        def _read_images():
            files = get_files(Config.ASSET_DIR + 'img/', '')
            images = {}
            for item in files:
                images.update({item: Config.ASSET_DIR + 'img/' + item})
            return {'img': images}

        @staticmethod
        def _read_javascript():
            files = get_files(Config.ASSET_DIR + 'js/', 'js')
            javascript = {}
            for item in files:
                js = read_file(Config.ASSET_DIR + 'js/' + item)
                javascript.update({item: str(js)})
            return {'js': javascript}

        @staticmethod
        def _read_media():
            files = get_files(Config.ASSET_DIR + 'media/', '')
            media = {}
            for item in files:
                media.update({item: Config.ASSET_DIR + 'media/' + item})
            return {'media': media}

        @staticmethod
        def _read_cert():
            try:
                return {'cert': Config.CERT_DIR + get_files(Config.CERT_DIR, 'crt')[0],
                        'key': Config.CERT_DIR + get_files(Config.CERT_DIR, 'key')[0]}
            except IndexError:
                return {'cert': None, 'key': None}

    Config.settings = SettingsReader().settings