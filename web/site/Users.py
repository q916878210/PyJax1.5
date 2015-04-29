__author__ = 'Sean Mead'


from jax.core.modules.Decorators import Database


@Database
class Users(object):
    def __init__(self):
        self.username = 'text primary key'
        self.password = 'text'

    def exists(self, username):
        r = self.query("SELECT COUNT(*) as count FROM Users WHERE username = ?", (username,))
        if r:
            return r[0][0] > 0

    def append_user(self, username, password):
        self.query("INSERT into Users (username, password) VALUES (?, ?)", (username, password))

    def get_password(self, username):
        r = self.query("SELECT password FROM Users WHERE username = ?", (username,))
        if r:
            return r[0][0]


class Static(type):
    users = Users()


def exists(username):
    return Static.users.exists(username)


def append_user(username, password):
    Static.users.append_user(username, password)


def get_password(username):
    return Static.users.get_password(username)
