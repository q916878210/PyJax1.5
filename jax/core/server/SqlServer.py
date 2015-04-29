"""
Created on Oct 1, 2014

@author: Sean Mead
"""

import socket
import ast
import time
import sqlite3 as sql
from threading import Thread
from os import path
from jax.core.modules.Log import Log
from jax.core.modules.Settings import Config
from jax.core.modules.Event import Event


class Database(object):
    def __init__(self, conn):
        self.__conn = conn
        self.__last = time.time()
        self.__locked = False

    @property
    def last(self):
        return self.__last

    @last.setter
    def last(self, last):
        self.__last = last

    @property
    def locked(self):
        return self.__locked

    @locked.setter
    def locked(self, lock):
        self.__locked = lock

    @property
    def conn(self):
        self.last = time.time()
        return self.__conn

    def execute(self, q, args):
        self.__locked = True
        cursor = self.conn.cursor()
        if args != 'None':
            cursor.execute(q, ast.literal_eval(args))
        else:
            cursor.execute(q)
        result = cursor.fetchall()
        self.__locked = False
        return result


class SqlMaster(object):
    TIMEOUT = 600000
    CLEAN = 'clean'
    CLEAR = 'clear'

    def __init__(self):
        self.__dbs = {}

    def __clear(self):
        keys = []
        for key, value in self.__dbs.iteritems():
            value.conn.close()
            keys.append(key)
        for key in keys:
            self.__dbs.pop(key)

    def __clean(self):
        keys = []
        exp = time.time() - SqlMaster.TIMEOUT
        for key, value in self.__dbs.iteritems():
            if not value.locked and (exp > value.last):
                value.conn.close()
                keys.append(key)
        for key in keys:
            self.__dbs.pop(key)

    def __add_database(self, db):
        self.__dbs.update({db: Database(sql.connect(db))})

    def __locate_db(self, db):
        if db not in self.__dbs:
            if path.exists(db):
                self.__add_database(db)
            else:
                return False
        return True

    def manage(self, args):
        if args == SqlMaster.CLEAN:
            self.__clean()
        elif args == SqlMaster.CLEAR:
            self.__clear()

    def execute(self, db, q, args):
        result = None
        try:
            if self.__locate_db(db):
                result = self.__dbs[db].execute(q, args)
        except Exception as e:
            Log.report_error(e.message)
        return result


class SqlConnectionHandler(object):
    def __init__(self, connection, address):
        self.__connection = connection
        self.__address = address
        self.db = None
        self.q = None

    def __receive_line(self):
        line = ''
        char = ''
        while char != '\n':
            char = self.__connection.recv(1)
            line += char
        return line[:-1]

    def __send_line(self, text):
        self.__connection.send(str(text) + '\n')

    def begin(self):
        key = self.__receive_line()
        db = None
        q = None
        if key == SqlAccess.QUERY:
            db = self.__receive_line()
            q = self.__receive_line()
        args = self.__receive_line()
        return key, db, q, args

    def complete(self, response):
        self.__send_line(response)
        self.__connection.close()


class SqlServer(Thread):
    KEY = 'Jax:sql_server'
    INTERVAL = 300000

    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.__running = False
        self.__master = SqlMaster()
        self.__port = Config.get_server().get('sql_port')
        self.__server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.__name = 'Sql Server'

    @staticmethod
    def new():
        Event.remove_event(SqlServer.KEY)
        SqlAccess().send_manage(SqlMaster.CLEAR)
        return SqlServer()

    @staticmethod
    def manage_clean():
        SqlAccess().send_manage(SqlMaster.CLEAN)

    @property
    def name(self):
        return self.__name

    @property
    def running(self):
        return self.__running

    @running.setter
    def running(self, running):
        self.__running = running

    def run(self):
        Event.add_event(obj=SqlServer,
                        method='manage_clean',
                        interval=10,
                        key=SqlServer.KEY, start=True)
        self.__running = True
        try:
            self.__server.bind(('localhost', self.__port))
            self.__server.listen(100)
        except Exception as e:
            Log.report_error(e.message)
            self.__running = False
        while self.__running:
            try:
                response = None
                handler = SqlConnectionHandler(*self.__server.accept())
                key, db, q, args = handler.begin()
                if key == SqlAccess.MANAGE:
                    self.__master.manage(args)
                elif key == SqlAccess.QUERY:
                    response = self.__master.execute(db, q, args)
                handler.complete(response)
            except Exception as e:
                Log.report_error(e.message)
        Event.remove_event(SqlServer.KEY)
        self.__master.manage(SqlMaster.CLEAR)


class StaticSqlAccess(type):
    PORT = Config.get_server().get('sql_port')

    @staticmethod
    def set_port(port):
        StaticSqlAccess.PORT = port


class SqlAccess(socket.socket):
    QUERY = 'SqlAccess:Query'
    MANAGE = 'SqlAccess:Manage'

    def __init__(self):
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def __receive_line(self):
        line = ''
        char = ''
        while char != '\n':
            char = self.recv(1)
            line += char
        return line[:-1]

    def __send_line(self, text):
        self.send(str(text) + '\n')

    def send_manage(self, args=None):
        result = ''
        try:
            self.connect(('localhost', StaticSqlAccess.PORT))
            self.__send_line(SqlAccess.MANAGE)
            self.__send_line(args)
            result = self.__receive_line()
            self.close()
        except Exception as e:
            Log.report_error(e.message)
        return result

    def send_query(self, db, q, args=None):
        result = ''
        try:
            self.connect(('localhost', StaticSqlAccess.PORT))
            self.__send_line(SqlAccess.QUERY)
            self.__send_line(db)
            self.__send_line(q)
            self.__send_line(args)
            result = self.__receive_line()
            self.close()
        except Exception as e:
            Log.report_error(e.message)
        return result


def query(db, q, args=None):
    return SqlAccess().send_query(db, q, args)