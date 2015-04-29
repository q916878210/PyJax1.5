"""
Created on Jan 26, 2015

@author: Sean Mead
"""


class Attributes(object):
    def __init__(self):
        """
        Create a Req object.  The object holds arguments as a dictionary and a request path.
        """
        self.__build = True
        self.__path = ''
        self.__method = ''
        self.__arguments = {}

    @property
    def build(self):
        """
        :return:
        """
        return self.__build

    @build.setter
    def build(self, build):
        self.__build = build

    @property
    def path(self):
        """
        :return: The path of the request
        """
        return self.__path

    @path.setter
    def path(self, path):
        self.__path = path

    @property
    def method(self):
        """
        :return: The method of the request
        """
        return self.__method

    @method.setter
    def method(self, method):
        self.__method = method

    @property
    def arguments(self):
        """
        :return: The request arguments
        """
        return self.__arguments