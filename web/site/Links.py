"""
Created on Oct 1, 2014

@author: Sean Mead
"""

from jax.core.modules.BaseLinks import BaseLinks
from jax.core.modules import Session, Stream
from jax.core.modules.Settings import Config
from jax.core.modules.Decorators import IsPost, IsValid
from web.site import Users


RES = Config.load_dir('web/html_part')

CONFIG = Config.load_dir('web/html_part/config')
FRAMEWORK = Config.load_dir('web/html_part/framework')
ASSETS = Config.load_dir('web/html_part/assets')
SITE = Config.load_dir('web/html_part/site')


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
        """
        Called each time the website is refreshed/loaded completely.
        :return:
        """
        if Session.valid(self.handler):
            return '<script>%s</script>' % RES['account_in.js']
        else:
            return '<script>%s</script>' % RES['account_out.js']

    def config(self):
        a = self.handler.get_argument('a') + '.html'
        if a in CONFIG:
            return CONFIG[a]

    def frame(self):
        a = self.handler.get_argument('a') + '.html'
        if a in FRAMEWORK:
            return FRAMEWORK[a]

    def assets(self):
        a = self.handler.get_argument('a') + '.html'
        if a in ASSETS:
            return ASSETS[a]

    def site(self):
        a = self.handler.get_argument('a') + '.html'
        if a in SITE:
            return SITE[a]

    def color(self):
        c = self.handler.get_argument('c')
        return '<div class="%s">%s</div>' % (c, c)

    def home(self):
        if Session.valid(self.handler):
            self.handler.set_kwargs(account=RES['home_in.html'] % Session.get_name(self.handler))
        else:
            self.handler.set_kwargs(account='Super secret stuff... <a load href="#account">please sign in</a>')
        return False

    def testing(self):
        return '<br>' + '<br>'.join([item for item in dir(self) if not item.startswith('_')])

    @IsPost.decorate(on_fail='home')
    def test(self):
        return 'test'

    @IsValid.decorate(on_fail='home')
    def sign_out(self):
        Session.stop(self.handler)
        return 'True'

    @IsValid.decorate(negate=True)
    @IsPost.decorate(on_fail='home')
    def register(self):
        username = self.handler.get_argument('username')
        password = self.handler.get_argument('password')
        if not Users.exists(username):
            Users.append_user(username, password)
            Session.start(self.handler, username)
            return '{"status":"true"}'
        return '{"status":"false", "message":"username invalid"}'

    @IsValid.decorate(negate=True, on_fail='home')
    def account(self):
        return RES['account.html']

    @IsValid.decorate(negate=True)
    @IsPost.decorate(on_fail='home')
    def sign_in(self):
        username = self.handler.get_argument('username')
        password = self.handler.get_argument('password')
        if Users.exists(username):
            if Users.get_password(username) == password:
                Session.start(self.handler, username)
                return '{"status":"true"}'
        return '{"status":"false", "message":"invalid username or combo"}'

    @IsPost.decorate
    def upload(self):
        if Session.valid(self.handler):
            path = current_user_path(self.handler)
            self.handler.move_tmp(path)
        return 'True'

    def stream(self):
        Stream.handle(self.handler, self.handler.get_argument('filename'))