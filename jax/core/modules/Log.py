__author__ = 'Sean Mead'

import time
from jax.core.modules.Settings import LogPool, Config
from jax.core.modules.Writer import Writer


class Log(type):

    INTERVAL = 10

    last_message = 0
    do_proceed_message = False

    last_error = 0
    do_proceed_error = False

    last_socket_error = 0
    do_proceed_socket_error = False

    writer = Writer()

    @staticmethod
    def ready():
        [Log.report(msg) for msg in LogPool.msg]
        [Log.report_error(err) for err in LogPool.err]
        [Log.report_socket_error(address, request) for address, request in LogPool.sock]
        LogPool.msg, LogPool.err, LogPool.sock = [], [], []

    @staticmethod
    def proceed_message():
        now = time.time()
        if (now - Log.last_message) > Log.INTERVAL:
            Log.last_message = now
            Log.do_proceed_message = Config.get_tmp('log_message')
        return Log.do_proceed_message

    @staticmethod
    def proceed_error():
        now = time.time()
        if (now - Log.last_error) > Log.INTERVAL:
            Log.last_error = now
            Log.do_proceed_error = Config.get_tmp('log_error')
        return Log.do_proceed_error

    @staticmethod
    def proceed_socket_error():
        now = time.time()
        if (now - Log.last_socket_error) > Log.INTERVAL:
            Log.last_socket_error = now
            Log.do_proceed_socket_error = Config.get_tmp('log_socket_error')
        return Log.do_proceed_socket_error

    @staticmethod
    def set_writer(writer):
        Log.writer = writer

    @staticmethod
    def report(msg):
        if Log.proceed_message():
            Log.writer.add(Log.writer.msg, str(msg))

    @staticmethod
    def report_info(info):
        if Log.proceed_message():
            Log.writer.add(Log.writer.info, str(info))

    @staticmethod
    def report_error(err):
        if Log.proceed_error():
            Log.writer.add(Log.writer.err, str(err))

    @staticmethod
    def report_socket_error(address=None, traceback=None):
        if Log.proceed_socket_error():
            Log.writer.add(Log.writer.sock, '%s\n%s' % (address, traceback))