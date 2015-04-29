__author__ = 'seanmead'

from Queue import Queue
from threading import Thread


class Writer(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.__queue = Queue()
        self.__running = False

    @property
    def running(self):
        return self.__running

    @running.setter
    def running(self, running):
        self.__running = running

    def stop(self):
        self.running = False
        self.add(None)

    def run(self):
        self.running = True
        while self.running:
            item = self.__queue.get()
            if item[0]:
                item[0](*item[1])

    def add(self, func, *args):
        self.__queue.put([func, args], False)

    def sock(self, item):
        print item

    def err(self, item):
        print item

    def msg(self, item):
        print item

    def info(self, item):
        print item
