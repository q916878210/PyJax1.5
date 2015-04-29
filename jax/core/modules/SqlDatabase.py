"""
Created on Jan 30, 2014

@author: Sean Mead
"""


import sqlite3 as sql
import ast
from os import path
from jax.core.modules.Settings import Config
from jax.core.server.SqlServer import SqlAccess


DB_DEFAULT = 'database.db'
DB_PATH = Config.DB_DIR
DB_NAME = Config.get('database')
if not DB_NAME:
    DB_NAME = DB_DEFAULT
DB_ABS = path.join(DB_PATH, DB_NAME)


HIDDEN = ['_']


class F(type):
    @staticmethod
    def hidden(item):
        for h in HIDDEN:
            if str(item).startswith(h):
                return True
        return False


class SqlDb(object):
    def __init__(self, schema):
        self.__schema = schema
        self.__create()
        self.__columns = self.__schema.columns.keys()

    @property
    def schema(self):
        return self.__schema

    @property
    def columns(self):
        return self.__columns

    def connect(self):
        return sql.connect(self.__schema.db)

    def query(self, q, args=None):
        result = SqlAccess().send_query(self.__schema.db, q, args)
        if result:
            result = ast.literal_eval(result)
        return result

    def __create(self):
        with self.connect() as conn:
            conn.executescript(self.__schema.ddl)


class Template(type):
    DDL = 'create table if not exists {0}(\n\t{1}\n);'

    @staticmethod
    def table_line(key, value):
        return key + '\t' + value

    @staticmethod
    def get_table(name, columns):
        return Template.DDL.format(name, ',\n\t'.join([Template.table_line(*item) for item in columns.items()]))


class TableScheme(object):
    def __init__(self, cls, dct, database=None):
        if not database:
            database = DB_NAME
        self.__db = path.join(DB_PATH, database)
        self.__valid = path.exists(self.__db)
        self.__name = str(cls.__name__)
        self.__columns = {item: dct[item] for item in [key for key in dct if not F.hidden(key)] if item in dct}
        self.__ddl = Template.get_table(self.__name, self.__columns)

    @property
    def db(self):
        return self.__db

    @property
    def valid(self):
        return self.__valid

    @property
    def name(self):
        return self.__name

    @property
    def columns(self):
        return self.__columns

    @property
    def ddl(self):
        return self.__ddl
