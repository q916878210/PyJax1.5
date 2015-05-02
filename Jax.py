"""
Created on Jan 26, 2015

@author: Sean Mead
"""

import argparse
import signal
import time
import sys
from threading import Thread

from jax.core.modules import Broadcast, Session
from jax.core.modules.Settings import Config, get_files
from jax.core.modules.Log import Log
from jax.core.modules.Tools import File, set_title, open_in_browser, get_address_local
from jax.core.modules.Input import Order, CallbackFlag, Interactive, InteractivePanel
from jax.core.modules.Event import Event
from jax.core.modules.SqlDatabase import DB_ABS
from jax.core.server.WebServer import WebServerThread
from jax.core.server.WebSocketServer import WebSocketThread
from jax.core.server.SocketClients import SocketUpdateThread
from jax.core.server.SqlServer import SqlServer, query as access_query
from jax.core.server.GhostServer import Ghost


class Service(object):
    def __init__(self, args):
        self.__running = False
        self.__args = args
        print 'service created'
        self.__menu = InterfaceFactory.menu(False, self.__args)
        print 'services started: %s:%s' % (Config.get_server()['address'], Config.get_server()['web_port'])
        signal.signal(signal.SIGINT, self.quit)

    def quit(self, arg=None, single=None, frame=None):
        self.__running = False

    def run(self):
        self.__running = True
        print 'holding...'
        while self.__running:
            time.sleep(60)
        self.__menu.quit()


class Schedule(type):
    KEY = 'Jax:schedule'

    @staticmethod
    def process_sessions():
        now = time.time()
        keys = [key for key in Session.Static.SESSIONS.keys() if Session.Static.SESSIONS[key][1] < now]
        for key in keys:
            Session.Static.SESSIONS.pop(key)

    @staticmethod
    def process_tmp():
        keys = Event.get_keys()
        to_del = [File(Config.TMP_DIR + item)
                  for item in get_files(Config.TMP_DIR) if item not in keys]
        for item in to_del:
            try:
                item.delete()
            except Exception as e:
                Log.report_error(e.message)

    @staticmethod
    def process():
        Schedule.process_sessions()
        Schedule.process_tmp()


class ToggleServer(type):
    @staticmethod
    def on(server):
        if not server.running:
            Log.report('Starting: %s' % server.name)
            try:
                server.start()
            except Exception as e:
                Log.report_error(e.message)

    @staticmethod
    def off(server):
        if server.running:
            Log.report('Stopping: %s' % server.name)
            try:
                server.running = False
                server.join(0)
            except Exception as e:
                Log.report_error(e.message)


class InterfaceFactory(type):

    @staticmethod
    def servers(cli=True, *args):
        return servers_factory(InteractivePanel if cli else Interactive, *args)

    @staticmethod
    def sql(cli=True):
        return sql_factory(InteractivePanel if cli else Interactive)

    @staticmethod
    def menu(cli=True, *args):
        return menu_factory(InteractivePanel if cli else Interactive, *args)


def servers_factory(inherit, *args):
    class Servers(inherit):
        def __init__(self, url):
            super(self.__class__, self).__init__(hide=['running'], prompt='Server: ', sub=True)
            self.__c_switch = CallbackFlag.as_switch(begin=self.__callback_pre)
            self.__choices = ['web', 'socket', 'socket_update', 'sql', 'ghost']
            self.__dict = dict(zip(self.__choices,
                                   [WebServerThread(url),
                                    WebSocketThread(),
                                    SocketUpdateThread(),
                                    SqlServer(),
                                    Ghost()]))

        def running(self, item):
            if item in self.__dict:
                return self.__dict[item].running
            return False

        def __callback_pre(self):
            Log.set_writer(self.get_writer())

        def callback(self, code, *args):
            self.__c_switch.switch(code, *args)

        def header(self):
            running = (['web', self.__dict['web'].running],
                       ['socket', self.__dict['socket'].running],
                       ['socket_update', self.__dict['socket_update'].running],
                       ['sql', self.__dict['sql'].running],
                       ['ghost', self.__dict['ghost'].running])
            msg = ''
            for status in running:
                msg += '\n%s: %s' % (' ' * (13 - len(status[0])) + status[0], 'Running' if status[1] else 'Stopped')
            return '\t____%s____%s' % ('Servers', msg)

        def kill_all(self, arg=None):
            for server in self.__dict.itervalues():
                if server.running:
                    ToggleServer.off(server)

        @Order(1)
        def start(self, arg=None):
            if arg in self.__dict:
                ToggleServer.off(self.__dict[arg])
                self.__dict[arg] = self.__dict[arg].new()
                ToggleServer.on(self.__dict[arg])

        @Order(2)
        def stop(self, arg=None):
            if arg in self.__dict:
                ToggleServer.off(self.__dict[arg])

    return Servers(*args)


def sql_factory(inherit):
    class Sql(inherit):
        def __init__(self):
            super(self.__class__, self).__init__(sub=True, prompt='Input: ')
            self.__c_switch = CallbackFlag.as_switch(begin=self.__callback_pre)
            self.__db = DB_ABS

        def header(self):
            return '\t____%s____\n%s' % ('Sql', self.__db.split('/')[-1])

        def set_db(self, db=None):
            if db:
                self.__db = db

        def query(self, q=None):
            if q:
                Log.report_info(access_query(self.__db, q))
            else:
                Log.report_error('empty query')

        def __callback_pre(self):
            Log.set_writer(self.get_writer())

        def callback(self, code, *args):
            self.__c_switch.switch(code, *args)

    return Sql()


def menu_factory(inherit, *args):
    class Menu(inherit):
        @staticmethod
        def schedule_events():
            Event.add_event(obj=Schedule, method='process', interval=30, key=Schedule.KEY, start=True)

        def __init__(self, arguments):
            super(self.__class__, self).__init__(hide=['back', 'schedule_events'], prompt='Input: ')
            try:
                signal.signal(signal.SIGINT, self.quit)
            except ValueError:
                pass
            self.looping = False
            self.__c_switch = CallbackFlag.as_switch(begin=self.__callback_begin, pre=self.__callback_pre)
            self.__title = Config.get('title')
            self.__url = None
            self.__servers = None
            self.__sql = None
            self.__cli = arguments.no_cli

            Menu.schedule_events()
            self.__load_args(arguments)

        def __init__post(self):
            _server = Config.get_server()
            self.__url = 'https://' if Config.get('cert') and Config.get('key') else 'http://'
            self.__url += '%s:%s' % (_server['address'], _server['web_port'])
            self.__servers = InterfaceFactory.servers(self.__cli, self.__url)
            self.__sql = InterfaceFactory.sql(self.__cli)

        def __load_args(self, args):
            set_title(self.__title)
            Session.resume()
            if args.localhost:
                Config.load_server(address=get_address_local())

            self.__init__post()

            if not args.no_web:
                self.__servers.start('web')
            if args.socket:
                self.__servers.start('socket')
            if args.socket_update:
                self.__servers.start('socket_update')
            if args.sql:
                self.__servers.start('sql')
            if args.ghost:
                self.__servers.start('ghost')
            if args.log_all:
                Config.load_tmp(log_socket_error=True)
                Config.load_tmp(log_error=True)
                Config.load_tmp(log_message=True)
            else:
                if args.log_disconnect:
                    Config.load_tmp(log_socket_error=True)
                if args.log_error:
                    Config.load_tmp(log_error=True)
                if args.log_message:
                    Config.load_tmp(log_message=True)

        def __callback_begin(self):
            self.__callback_pre()
            Log.ready()

        def __callback_pre(self):
            Log.set_writer(self.get_writer())

        def callback(self, code, *args):
            self.__c_switch.switch(code, *args)

        def header(self):
            items = [['message', Config.get_tmp('log_message')],
                     ['error', Config.get_tmp('log_error')],
                     ['disconnect', Config.get_tmp('log_socket_error')]]
            msg = [item[0] for item in items if item[1]]
            if len(msg) == 0:
                msg = ['off']
            return "\t____%s____\n%s\nLogging: %s" % (self.__title, self.__url, ', '.join(msg))

        def open_in_browser(self, arg=None):
            open_in_browser(arg, self.__url)
            self.pane.clear_input()

        @Order(2)
        def servers(self, arg=None):
            self.__servers.loop()
            self.resize()

        @Order(3)
        def sql(self, db=None):
            if self.__servers.running('sql'):
                if db:
                    self.__sql.set_db(db)
                self.__sql.loop()
                self.resize()

        @staticmethod
        def toggle_disconnect(arg=None):
            if Config.get_tmp('log_socket_error'):
                Config.load_tmp(log_socket_error=False)
            else:
                Config.load_tmp(log_socket_error=True)
            Log.last_socket_error = 0

        @staticmethod
        def toggle_message(arg=None):
            if Config.get_tmp('log_message'):
                Config.load_tmp(log_message=False)
            else:
                Config.load_tmp(log_message=True)
            Log.last_message = 0

        @staticmethod
        def toggle_error(arg=None):
            if Config.get_tmp('log_error'):
                Config.load_tmp(log_error=False)
            else:
                Config.load_tmp(log_error=True)
            Log.last_error = 0

        @Order(1)
        def reload(self, arg=None):
            Broadcast.send('reload')

        @Order(0)
        def quit(self, arg=None, single=None, frame=None):
            Session.save()
            self.__servers.kill_all()
            self.looping = False

    return Menu(*args)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="PyJax")
    parser.add_argument('--no-web', action='store_true')
    parser.add_argument('--localhost', action='store_true')
    parser.add_argument('--socket', action='store_true')
    parser.add_argument('--socket_update', action='store_true')
    parser.add_argument('--sql', action='store_true')
    parser.add_argument('--ghost', action='store_true')
    parser.add_argument('--log-disconnect', action='store_true')
    parser.add_argument('--log-error', action='store_true')
    parser.add_argument('--log-message', action='store_true')
    parser.add_argument('--log-all', action='store_true')
    parser.add_argument('--no-cli', action='store_false')
    parser.add_argument('--service', action='store_true')
    p_args = parser.parse_args()
    if p_args.service:
        service = Service(p_args)
        service.run()
    else:
        InterfaceFactory.menu(p_args.no_cli, p_args).loop()