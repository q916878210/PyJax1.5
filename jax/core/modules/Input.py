__author__ = 'Sean Mead'

import signal
from itertools import izip
from types import FunctionType, MethodType
from jax.core.modules.Tools import PlatformHolder
from jax.core.modules.Writer import Writer
from jax.core.modules.Callback import Callback


if not PlatformHolder.is_windows():
    import curses
    from curses import panel
else:
    curses = None
    panel = None


class Order(object):
    def __init__(self, order=0):
        self.order = order

    def __call__(self, func):
        def func_wrapper(_self, *args, **kwargs):
                return func(_self, *args, **kwargs)
        func_wrapper.__setattr__('wrapper_order', self.order)
        return func_wrapper


class Input(type):
    @staticmethod
    def screen_input(screen, r, c, prompt_string, key):
        screen.addstr(r, c, prompt_string)
        screen.addstr(r + 1, c, chr(key))
        curses.echo()
        screen.refresh()
        item = screen.getstr(r + 1, c + 1, 20)
        return item

    class Choice(object):
        def __init__(self, text):
            self.__text = text
            self.__name = None
            self.__args = []

        @property
        def text(self):
            return self.__text

        @text.setter
        def text(self, text):
            self.__text = text

        @property
        def name(self):
            return self.__name

        @name.setter
        def name(self, name):
            self.__name = name

        @property
        def args(self):
            return self.__args

        @args.setter
        def args(self, args):
            self.__args = args

    @staticmethod
    def pause():
        raw_input("\ncontinue")

    @staticmethod
    def check(prompt="?"):
        response = raw_input(prompt)
        return "y" in response

    @staticmethod
    def choice(prompt='?', choices=[], zero=1):
        choice_string = ''
        for i in range(1, len(choices)+1):
            choice_string += '%s: %s\n' % (i, choices[i-1])
        response = Input.Choice(raw_input('%s\n%s' % (choice_string, prompt)))
        if response.text == ".r":
            return None
        try:
            val = int(str(response.text.split(' ', 1)[0]).strip())
            if len(choices) >= val >= zero:
                response.name = choices[val-zero]
                if len(response.text) > len(str(val)):
                    response.args = response.text.split(str(val), 1)[-1].strip()
                return response
            else:
                return Input.choice(prompt, zero)
        except ValueError:
            for choice in choices:
                if choice in response.text:
                    response.name = choice
                    response.args = response.text.split(choice, 1)[1].strip()
                    return response


class CallbackFlag(Callback):
    BEGIN, END, PRE, POST, ERR = 0, 1, 2, 3, 4

    __c_list = None

    @staticmethod
    def as_list():
        if not CallbackFlag.__c_list:
            CallbackFlag.__c_list = \
                [CallbackFlag.BEGIN, CallbackFlag.END, CallbackFlag.PRE, CallbackFlag.POST, CallbackFlag.ERR]
        return CallbackFlag.__c_list

    @staticmethod
    def as_dict(begin=None, end=None, pre=None, post=None, err=None):
        return dict(izip(CallbackFlag.as_list(), [begin, end, pre, post, err]))

    @staticmethod
    def as_switch(begin=None, end=None, pre=None, post=None, err=None):
        return CallbackFlag.Switch(CallbackFlag.as_dict(begin, end, pre, post, err))


class Interactive(object):
    def __init__(self, header='Header', prompt='Select: ', hide=None, *args, **kwargs):
        self.__writer = None
        self.__header = header
        self.__prompt = prompt
        self.__hide = ['prompt', 'loop', 'callback', 'header', 'get_writer', '_']
        if hide:
            self.__hide += hide
        functions = {item: self.__getattribute__(item) for item in dir(self) if not self.__hidden(item)}
        self.functions = {key: value for key, value in functions.iteritems() if type(value) in [FunctionType, MethodType]}
        self.choices = sorted(self.functions.keys())
        self.choices = [item.replace('_', ' ') for item in sorted(self.choices, key=self.__func_attribute)]
        self.__string = ''
        for index, key in enumerate(self.choices):
            self.__string += '%s: %s\n' % (index + 1, key)
        self.looping = False

    def get_writer(self):
        return self.__writer

    def __str__(self):
        return self.__string

    def __func_attribute(self, item):
        if 'wrapper_order' in dir(self.functions.get(item)):
            return int(self.functions.get(item).__getattribute__('wrapper_order'))
        return len(self.choices)

    def __hidden(self, item):
        for hidden in self.__hide:
            if str(item).startswith(hidden):
                return True
        return False

    def callback(self, status, arg=None):
        pass

    def header(self):
        return self.__header

    def prompt(self):
        return self.__prompt

    @Order(0)
    def back(self, *args):
        self.looping = False

    def loop(self):
        self.__writer = Writer()
        self.__writer.start()
        self.looping = True
        self.callback(CallbackFlag.BEGIN)
        while self.looping:
            try:
                self.callback(CallbackFlag.PRE)
                print self.header()
                choice = Input.choice(self.prompt(), self.choices)
                choice.name = choice.name.replace(' ', '_')
                if len(choice.args) > 0:
                    b = self.__getattribute__(choice.name)(choice.args)
                else:
                    b = self.__getattribute__(choice.name)()
                if str(b).lower() == 'break':
                    self.looping = False
                self.callback(CallbackFlag.POST)
            except Exception as e:
                self.callback(CallbackFlag.ERR, e)
        self.__writer.stop()
        self.callback(CallbackFlag.END)

if not PlatformHolder.is_windows():
    class InteractivePanel(Interactive):
        class PaneWriter(Writer):
            def __init__(self):
                Writer.__init__(self)
                self.__pane_writer = None

            @property
            def pane_writer(self):
                return self.__pane_writer

            @pane_writer.setter
            def pane_writer(self, pane_writer):
                self.__pane_writer = pane_writer

            def sock(self, item):
                if self.pane_writer:
                    self.pane_writer(item, curses.color_pair(2))

            def err(self, item):
                if self.pane_writer:
                    self.pane_writer(item, curses.color_pair(1))

            def msg(self, item):
                if self.pane_writer:
                    self.pane_writer(item)

            def info(self, item):
                if self.pane_writer:
                    self.pane_writer(item, curses.color_pair(3))

        class CursesPane(object):
            def __init__(self, screen, prompt, logs):
                self.block = True
                self.__screen = screen
                self.__prompt = prompt
                self.__height, self.__width = self.__screen.getmaxyx()

                self.__header = self.__screen.subwin(5, 0, 0, 0)
                self.__menu = self.__screen.subwin(0, 36, 6, 0)
                self.__log = self.__screen.subwin(0, 0, 6, 36)

                curses.start_color()
                curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
                curses.init_pair(2, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
                curses.init_pair(3, curses.COLOR_GREEN, curses.COLOR_BLACK)
                curses.init_pair(4, curses.COLOR_YELLOW, curses.COLOR_BLACK)
                curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)

                self.__menu_height = self.__height - 6
                self.__menu_width = 36

                self.__log_height = self.__height - 6 - 2
                self.__log_width = self.__width - 36 - 2

                self.__menu.keypad(1)
                self.__header.keypad(1)
                self.__log.keypad(1)
                self.__focus_pos = 0
                self.__logs = logs
                self.__key_input = []
                self.__deletes = ['127', curses.KEY_BACKSPACE, curses.KEY_DC]
                self.__punctuation = [' ', '/', '.', '*', '"', "'", '(', ')', ';']
                self.panel_header = panel.new_panel(self.__header)
                self.panel_window = panel.new_panel(self.__menu)
                self.panel_log = panel.new_panel(self.__log)
                self.panel_header.hide()
                self.panel_window.hide()
                self.panel_log.hide()
                panel.update_panels()

            def clear_input(self):
                self.__focus_pos = 0
                self.__header.clear()

            def clear_menu(self):
                self.__menu.clear()

            def get_input(self):
                return self.__key_input

            def focus_input(self):
                prompt = self.__prompt()
                prompt_len = len(prompt) + 3

                self.__header.addstr(2, 3, prompt, curses.color_pair(5))
                curses.echo()
                self.__header.refresh()
                self.block = False
                self.write_log('')
                item = self.__header.getch(2, prompt_len + self.__focus_pos)
                self.block = True
                is_a = False
                l = 1
                try:
                    is_a = chr(item).isalpha()
                    l = len(repr(item))
                    if chr(item) in self.__punctuation:
                        is_a = True
                except Exception as e:
                    is_a = False

                if is_a:
                    self.__focus_pos += 1
                else:
                    self.__header.addstr(2, prompt_len + self.__focus_pos, ' '*l)

                if repr(item) in self.__deletes and self.__focus_pos >= 1:
                    self.__focus_pos -= 1
                    self.__header.addstr(2, prompt_len + self.__focus_pos, ' ')
                    del self.__key_input[-1]

                self.__header.refresh()

                if is_a:
                    self.__key_input.append(chr(item))
                    return None
                return item

            def display(self):
                self.panel_header.top()
                self.panel_window.top()
                self.panel_log.top()
                self.panel_header.show()
                self.panel_window.show()
                self.panel_log.show()
                self.__log.clear()
                self.__refresh_log()
                self.__header.clear()
                self.__header.box()
                self.__header.refresh()
                self.__menu.clear()

            def hide(self):
                self.__header.clear()
                self.__menu.clear()
                self.__log.clear()
                self.panel_header.hide()
                self.panel_window.hide()
                self.panel_log.hide()
                panel.update_panels()
                curses.doupdate()

            def write_menu(self, header, choices, position):
                headers = header.split('\n')
                offset = len(headers)
                for index, item in enumerate(headers):
                    item_str = item + (' ' * (self.__menu_width - len(item)))
                    self.__menu.addstr(index, 1, item_str, curses.color_pair(4))
                for index, item in enumerate(choices):
                    if index == position:
                        mode = curses.A_REVERSE
                    else:
                        mode = curses.A_NORMAL

                    msg = '%d. %s' % (index + 1, item)
                    self.__menu.addstr(offset+index + 1, 1, msg, mode)
                self.__menu.refresh()

            def __refresh_log(self):
                try:
                    self.__log.box()
                    self.__log.addstr(0, 1, 'Log', curses.A_NORMAL)
                except Exception:
                    pass
                self.__log.refresh()

            def check_write_log(self, log=None, mode=curses.A_NORMAL):
                if self.block:
                    self.__logs.insert(0, [log, mode])
                else:
                    self.write_log(log, mode)

            def write_log(self, log=None, mode=curses.A_NORMAL):
                if log:
                    self.__logs.insert(0, [log, mode])
                try:
                    for index, log_item in enumerate(self.__logs):
                        log_str = log_item[0]
                        if len(log_str) > self.__log_width:
                            log_str = log_str[:self.__log_width - 3] + '...'
                        self.__log.addstr(index + 1, 1, log_str + ' ' * (self.__log_width - len(log_str)), log_item[1])
                except Exception:
                    if len(self.__logs) > 100:
                        for i in range(100, len(self.__logs)):
                            del self.__logs[100]
                self.__log.box()
                self.__log.addstr(0, 1, 'Log', curses.A_NORMAL)
                self.__log.refresh()
                self.__header.refresh()

            @property
            def menu(self):
                return self.__menu

            @property
            def header(self):
                return self.__header

        def __init__(self, hide=None, sub=False, **kwargs):
            Interactive.__init__(self, hide=['CursesPane', 'logs', 'resize'] + (hide if hide else []), **kwargs)
            self.__writer = None
            self.__logs = []
            self.__sub = sub
            self.__input = {
                curses.KEY_ENTER: self.__enter,
                ord('\n'): self.__enter,
                curses.KEY_UP: self.__up,
                curses.KEY_DOWN: self.__down,
                curses.KEY_RESIZE: self.resize}
            self.screen = None
            self.pane = None

        def get_writer(self):
            return self.__writer

        @property
        def logs(self):
            return self.__logs

        def __close(self):
            if not self.__sub:
                curses.nocbreak()
                self.screen.keypad(0)
                curses.echo()
                curses.endwin()

        def __enter(self, p):
            arg = ''.join(self.pane.get_input())
            self.functions.get(self.choices[p].replace(' ', '_'))(arg)
            return p

        def __up(self, p):
            return p - 1 if p > 0 else 0

        def __down(self, p):
            return p + 1 if p < len(self.choices) - 1 else len(self.choices) - 1

        def resize(self, p=None):
            self.pane.hide()
            self.pane = InteractivePanel.CursesPane(self.screen, self.prompt, self.__logs)
            self.pane.display()
            return p

        def loop(self):
            self.looping = True
            self.screen = curses.initscr()
            curses.noecho()
            self.pane = InteractivePanel.CursesPane(self.screen, self.prompt, self.__logs)
            self.__writer = InteractivePanel.PaneWriter()
            self.__writer.pane_writer = self.pane.check_write_log
            self.pane.display()
            self.__writer.start()
            position = 0
            loop_count = 0
            self.callback(CallbackFlag.BEGIN)
            while self.looping:
                try:
                    signal.signal(signal.SIGINT, self.back)
                    self.callback(CallbackFlag.PRE)
                    self.pane.write_menu(self.header(), self.choices, position)
                    curses.doupdate()
                    key = self.pane.focus_input()
                    if key:
                        if key in self.__input:
                            position = self.__input[key](position)
                        else:
                            try:
                                if chr(key).isalnum():
                                    new_pos = int(chr(key)) - 1
                                    if 0 <= new_pos < len(self.choices):
                                        position = new_pos
                            except Exception as e:
                                self.callback(CallbackFlag.ERR, e)
                    self.callback(CallbackFlag.POST)
                    curses.doupdate()
                except Exception as e:
                    self.callback(CallbackFlag.ERR, e)
                loop_count += 1
            self.__writer.stop()
            self.pane.hide()
            self.__close()
            self.callback(CallbackFlag.END)

else:
    InteractivePanel = Interactive