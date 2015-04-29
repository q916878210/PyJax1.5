"""
Created on Oct 1, 2014

@author: Sean Mead
"""

from jax.core.modules.BaseLinks import BaseLinks
from jax.core.modules import Session, Stream
from jax.core.modules.Settings import Config
from jax.core.modules.Decorators import IsPost
from web.site.WebData import Html, Script
from web.site import Users


def current_user_path(handler):
    """
    Return the full path to the User folder.
    :param handler: the self.__handler of the Links object.
    """
    return Config.USER_DIR + Session.get_name(handler) + '/'


class Links(BaseLinks):
    def __init__(self, handler):
        BaseLinks.__init__(self, handler)
        """
        Create a links object used to handle url paths.
        :param handler: the handler of the client
        """

    def refresh_script(self):
        if Session.valid(self.handler):
            return Script.account_in(Session.get_name(self.handler))
        else:
            return Script.account_out

    def orange(self):
        return '<style>#side{background:#FF8800;}</style>'

    def red(self):
        return '<style>#side{background:#FF4444;}</style>'

    def blue(self):
        return '<style>#side{background:#4690ee;}</style>'

    def home(self):
        if Session.valid(self.handler):
            self.handler.set_kwargs(account=Html.home(Session.get_name(self.handler)))
        else:
            self.handler.set_kwargs(account=Html.account)
        return False

    def testing(self):
        return '<br>' + '<br>'.join([item for item in dir(self) if not item.startswith('_')])

    @IsPost(on_fail='home')
    def test(self):
        return 'test'

    def sign_out(self):
        Session.stop(self.handler)
        return 'True'

    @IsPost(on_fail='home')
    def register(self):
        if not Session.valid(self.handler):
            username = self.handler.get_argument('username')
            password = self.handler.get_argument('password')
            if not Users.exists(username):
                Users.append_user(username, password)
                Session.start(self.handler, username)
                return '{"status":"true"}'
            return '{"status":"false", "message":"username invalid"}'

    def sign_in(self):
        if self.handler.POST:
            if not Session.valid(self.handler):
                username = self.handler.get_argument('username')
                password = self.handler.get_argument('password')
                if Users.exists(username):
                    if Users.get_password(username) == password:
                        Session.start(self.handler, username)
                        return '{"status":"true"}'
                return '{"status":"false", "message":"invalid username or combo"}'

    @IsPost
    def upload(self):
        if Session.valid(self.handler):
            path = current_user_path(self.handler)
            self.handler.move_tmp(path)
        return 'True'

    def stream(self):
        Stream.handle(self.handler, self.handler.get_argument('filename'))