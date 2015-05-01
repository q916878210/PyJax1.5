__author__ = 'Sean Mead'

import imp
from re import compile
from types import FunctionType, MethodType
from web import triggers
from jax.core.modules import Broadcast
from jax.core.modules.CssCompressor import compress as css_compress
from jax.core.modules.JsCompressor import compress as js_compress


class Node(object):
    def __init__(self, index, item, attr, callbacks):
        self.__tag = item[0] if item[1] else '/' + item[0]
        self.__indexes = [index, item[2]]
        self.__attr_str = attr
        self.__attributes = {}
        self.__callbacks = callbacks
        self.__parse_attr()

    def __str__(self):
        return self.tag

    def __add_attr(self, name, value):
        self.__attributes[name] = value

    def __parse_attr(self):
        q = ['"', "'"]
        keys = [_k for _k in HtmlParse.c.findall(self.__attr_str)]
        values = [_v for _v in HtmlParse.d.findall(self.__attr_str)]
        a_mod = self.__attr_str
        if len(keys) == len(values):
            for index, key in enumerate(keys):
                a_mod = a_mod.replace(key, '')
                a_mod = a_mod.replace(values[index], '')
                if values[index][0] in q and values[index][-1] in q:
                    values[index] = values[index][1:-1]
                self.__attributes[key] = values[index]
        [self.__add_attr(item, True) for item in a_mod.replace('=', '').split(' ') if item]

    @property
    def tag(self):
        return self.__tag

    @property
    def indexes(self):
        return self.__indexes

    @property
    def attr_str(self):
        return self.__attr_str

    @property
    def attr(self):
        return self.__attributes

    def inner(self):
        return self.__callbacks[2](self.__indexes)

    def get(self, attr):
        if attr in self.__attributes:
            return self.__attributes[attr]

    def find_all(self, tag):
        return [child for child in self.children() if child.tag == tag]

    def find(self, tag, start=0):
        _a = self.find_all(tag)
        return _a[start] if len(_a) > start else None

    def parent(self):
        return self.__callbacks[0](self.__indexes)

    def children(self):
        return self.__callbacks[1](self.__indexes)


class HtmlParse(object):
    a = '(<.*?>)'
    b = compile('([^\s]+)')
    c = compile(r'([A-Za-z]+)=')
    d = compile(r'=([^\s]+)')
    e = '([^(<*?>)]*)'

    def __init__(self, html, reg_master=a, reg_sup=None):
        self.html = html
        self.__keys = []
        self.__attr = []
        self.inner = None
        self.__all = self.__gen(compile('%s|%s' % (reg_master, reg_sup) if reg_sup else reg_master))
        self.__parse()

    def __str__(self):
        return '\n'.join(['%s %s' % (index, item) for index, item in enumerate(self.__all)])

    @property
    def keys(self):
        return self.__keys

    def select(self, selector):
        pass

    def search_all(self, term='', tag='*'):
        if tag != '*':
            r = [index for index, item in enumerate(self.keys) if item == tag]
            return [self.__node(index) for index in r if self.__search_attr(term, index)]
        else:
            return [self.__node(i) for i in range(0, len(self.keys)) if self.__search_attr(term, i)]

    def search(self, term='', tag='*'):
        if tag != '*':
            r = [index for index, item in enumerate(self.keys) if item == tag]
            for index in r:
                if self.__search_attr(term, index):
                    return self.__node(index)
        else:
            for i in range(0, len(self.keys)):
                if self.__search_attr(term, i):
                    return self.__node(i)

    def find_all(self, tag):
        return [self.__node(index) for index, item in enumerate(self.keys) if item == tag]

    def find(self, tag, start=0):
        if tag in self.keys:
            return self.__node(self.keys.index(tag, start))

    def __search_attr(self, term, index):
        if term.lower() in self.__attr[index]:
            return True

    def __node(self, index):
        return Node(index, self.__all[index], self.__attr[index],
                    (self.__parent_node, self.__children, self.get_inner))

    def get_inner(self, indexes):
        if not self.inner:
            self.inner = [item.groups()[1] for item in compile(self.a + self.e).finditer(self.html)]
        return self.inner[indexes[0]]

    def __children(self, indexes):
        if indexes[1] - indexes[0] > 1:
            return [self.__node(i) for i in range(indexes[0] + 1, indexes[1]) if not self.keys[i].startswith('/')]

    def __parent_node(self, indexes):
        if indexes[0] > 0:
            for i in range(indexes[0] - 1, -1, -1):
                if self.__all[i][2] > indexes[0]:
                    return self.__node(i)

    def __split_group(self, group):
        t = self.b.findall(group)
        name = t[0].strip('<>')
        if t[1:]:
            t[-1] = t[-1][:-2] + t[-1][-2:].strip('/>')

        self.__attr.append(' '.join(t[1:]))
        self.__keys.append(name)
        return [name.strip('/'), not name.startswith('/'), False]

    def __gen(self, reg_x):
        return [self.__split_group(item.group()) for item in reg_x.finditer(self.html)]

    def __find_closing(self, tag, index):
        if ('/' + tag[0]) in self.keys[index + 1:]:
            if tag in self.__all[index + 1:]:
                r = self.__all[index + 1:].index(tag) + index + 1
                i = self.keys[index + 1:].index('/' + tag[0]) + index + 1
                #self.__all[r][2] = self.__find_closing(self.__all[r], r)
                if i < r:
                    return i
                return self.__find_closing(tag, self.keys[index + 1:].index('/' + tag[0]) + index + 1)
            else:
                return self.keys[index + 1:].index('/' + tag[0]) + index + 1
        return index

    def __parse(self):
        for i in range(0, len(self.__all)):
            if self.__all[i][1]:
            #if self.__all[i][1] and not self.__all[i][2]:
                self.__all[i][2] = self.__find_closing(self.__all[i], i)


class InjectParse(object):
    KEY_I = '!'
    a = compile('({*%(.*?)%*})')

    def __init__(self, text, k2=False):
        self.__k2 = k2
        self.__text = text
        self.__inserts = {}
        self.__triggers = {}
        self.__group()

    @property
    def inserts(self):
        return self.__inserts

    @property
    def triggers(self):
        return self.__triggers

    def __group(self):
        for i, t in self.a.findall(self.__text):
            if t:
                if t.startswith(self.KEY_I):
                    self.__inserts[t[len(self.KEY_I):]] = i
                else:
                    o = self.__parse_trigger(triggers, t.split('.'))
                    if type(o) in [FunctionType, MethodType]:
                        self.__triggers[i] = o

    def __parse_trigger(self, o, arg):
        if len(arg) > 0 and arg[0] in dir(o):
            o = getattr(o, arg[0])
            return self.__parse_trigger(o, arg[1:])
        return o


class HtmlInjectParse(HtmlParse):
    def __init__(self, html, k2=False):
        super(self.__class__, self).__init__(html, reg_sup='({*%(.*?)%*})')
        self.__ip = InjectParse(html, k2)

    @property
    def inject(self):
        return self.__ip

    def __mod_node(self, node, func):
        def _func():
            if func.func_code.co_argcount == 1:
                return func(node)
        node.__setattr__('function', _func)

    def __mod_nodes(self, nodes, func):
        for node in nodes:
            self.__mod_node(node, func)
        return nodes

    def get_inner(self, indexes=None):
        if not self.inner:
            self.inner = [item.groups()[1] for item in compile(self.a + self.e).finditer(self.html)]
            for key in self.__ip.inserts.keys():
                for node in self.find_all(self.__ip.inserts[key]):
                    self.inner.insert(node.indexes[0], '')
            for key in self.__ip.triggers.keys():
                for node in self.find_all(key):
                    self.inner.insert(node.indexes[0], '')
        if indexes:
            return self.inner[indexes[0]]

    def find_insert(self, key):
        if key in self.__ip.inserts:
            return self.find(self.__ip.inserts[key])

    def find_insert_all(self, key):
        if key in self.__ip.inserts:
            return self.find_all(self.__ip.inserts[key])

    def get_triggers(self):
        return [self.__mod_nodes(self.find_all(key), func) for key, func in self.__ip.triggers.iteritems()]


class Mini(type):

    @staticmethod
    def js(text):
        return js_compress(text)

    @staticmethod
    def css(text):
        return css_compress(text)


def do_load(msg):
    imp.reload(triggers)

Broadcast.register(do_load)