__author__ = 'seanmead'

import socket
from threading import Thread

from jax.core.modules.Event import Event
from jax.core.modules.Settings import Config
from jax.core.modules.Log import Log


class Manager(type):
    HEARTBEAT = 90
    Clients = {}

    @staticmethod
    def status():
        return 'Connections:\t\t%s\nHeart Signal:\t\t%s\n' % (len(Manager.Clients), len(Event.get_events()))

    @staticmethod
    def events():
        Event.print_events()

    class Code(type):
        PUSH = 0
        HEARTBEAT = 1


class State(type):
    active = False


class Ghost(object):
    SERVER = 'server'
    ACCESS = 'access'
    UPDATE = 'update'

    def __init__(self):
        _server = Config.get_server()
        self.__congress = [Threaded(ghost=Ghost.SERVER, ip=_server['address'], port=_server['ghost_port']),
                           Threaded(ghost=Ghost.UPDATE, port=_server['ghost_update_port'])]
        self.__name = 'Ghost Server'

    @staticmethod
    def new():
        return Ghost()

    @property
    def name(self):
        return self.__name

    @property
    def running(self):
        return State.active

    @running.setter
    def running(self, running):
        State.active = running

    @staticmethod
    def clean():
        for client in Manager.Clients.values():
            client.destroy()

    def start(self):
        State.active = True
        for ghosted in self.__congress:
            ghosted.start()

    def join(self, timeout):
        self.clean()
        for ghosted in self.__congress:
            ghosted.socket.shutdown(timeout)


class Client(object):
    def __init__(self, conn, address, account):
        """
        :rtype : Client
        """
        self.__conn = conn
        self.__address = address
        self.__account = account
        self.__process = None

    @staticmethod
    def send_to(account='', data=''):
        if account in Manager.Clients:
            Manager.Clients.get(account).send(data)
        else:
            Event.remove_event(account, True)

    def send(self, data=''):
        try:
            self.__conn.send('%s\n' % data)
        except Exception:
            self.__conn.close()
            Manager.Clients.pop(self.__account)


class Ghosted(socket.socket):
    def __init__(self):
        """
        :rtype : Ghosted
        """
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)

    def burn(self):
        pass


class Access(Ghosted):
    def __init__(self, port=8944, account=None):
        Ghosted.__init__(self)
        if account:
            self.__buffer = 2048
            self.__ip = 'localhost'
            self.__port = port
            self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__account = account

    def burn(self):
        try:
            self.connect((self.__ip, self.__port))
            self.send(self.__account)
        except Exception:
            pass
        self.close()


class Server(Ghosted):
    def __init__(self, ip, port):
        Ghosted.__init__(self)
        self.__buffer = 2048
        self.__ip = ip
        self.__port = port
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def burn(self):
        try:
            self.bind((self.__ip, self.__port))
        except Exception as e:
            Log.report_error(e.message)
        Log.report('Ghost Server %s:%s' % (self.__ip, self.__port))
        self.listen(500)
        while State.active:
            try:
                conn, address = self.accept()
                account = conn.recv(1024).replace('\n', '')
                if account != '':
                    client = Client(conn, address, account)
                    Manager.Clients.update({account: client})
                    try:
                        Event.remove_event(account)
                        Event.add_event(obj=Client, method='send_to',
                                        key=account, start=True, interval=Manager.HEARTBEAT,
                                        args={'account': account, 'data': Manager.Code.HEARTBEAT})
                    except Exception as e:
                        Log.report_error(e.message)
            except Exception:
                State.active = False


class Update(Ghosted):
    def __init__(self, port=8944):
        Ghosted.__init__(self)
        self.__buffer = 2048
        self.__ip = 'localhost'
        self.__port = port
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def burn(self):
        try:
            self.bind((self.__ip, self.__port))
        except Exception:
            pass
        Log.report('Ghost Update %s:%s' % (self.__ip, self.__port))
        self.listen(500)
        while State.active:
            try:
                conn, address = self.accept()
                account = conn.recv(1024)
                if account and account in Manager.Clients:
                    Event.add_event(obj=Client, method='send_to', key=account, start=True,
                                    onetime=True, args={'account': account, 'data': Manager.Code.PUSH})
            except Exception:
                pass


class Threaded(Thread):
    def __init__(self, ghost, **kwargs):
        """
        :rtype : Threaded
        """
        Thread.__init__(self)
        self.daemon = True
        self.__ghost = ghost
        self.__kwargs = kwargs
        self.__socket = None

    @property
    def socket(self):
        """
        :rtype : Ghosted
        """
        return self.__socket

    @staticmethod
    def server(**kwargs):
        return Server(**kwargs)

    @staticmethod
    def access(**kwargs):
        return Access(**kwargs)

    @staticmethod
    def update(**kwargs):
        return Update(**kwargs)

    def run(self):
        self.__socket = getattr(Threaded, self.__ghost)(**self.__kwargs)
        self.__socket.burn()