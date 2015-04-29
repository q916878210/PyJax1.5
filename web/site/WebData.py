"""
Created on Oct 1, 2014

@author: Sean Mead

Everything in WebData is a shortcut for printing html or javascript.
"""


class Html(type):
    account = """
    <section class="pad-32-lr pad-16-tb">
    <h2 class="center">Sign in to access features</h2>
    <div class="small-push"></div>
    <div class="form-wrap no-select center">
        <img class="circle" src="avatar.png"/>
        <a name="status"></a>
        <form id="form" class="hide-label" action="sign_in" method="POST" onsubmit="signIn(this);">
            <label for="username">Username</label><input class="input-text" name="username" id="username" type="text" placeholder="Username"/>
            <label for="password">Password</label><input class="input-text" name="password" id="password" type="password" placeholder="Password"/>
            <label for="confirm">Password</label><input class="input-text" name="confirm" id="confirm" type="hidden" placeholder="Retype New Password"/>
            <div class="submit-holder"></div>
            <label for="submit">Sign in</label><input class="blue button" id="submit" type="submit" value="Sign in"/>
        </form>
        <div class="small-push">
            <a class="button blue-text" onclick="changeForm(this);">Create account</a>
        </div>
    </div>
</section>
    """


    @staticmethod
    def home(username):
        return """

        <style>
            #side{
                min-height: 200px;
            }
        </style>

<div class="split">
    <section class="pad-32-lr pad-16-tb">
        <h2 class="center">Welcome %s</h2>
        <div class="small-push"></div>
        <div class="buttons-block content-wrapper small">
            <a class="button" load="#side" href="#red">Red</a>
            <a class="button" load="#side" href="#blue">Blue</a>
            <a class="button" load="#side" href="#orange">Orange</a>
            <a class="button round blue" onclick="signOut();">Sign out</a>
        </div>
    </section>

    <section id="side" class="pad-32-lr">

    </section>
</div>
        """ % username


class Script(type):
    account_out = """
        <script>
        Jax.ready(function(){
            var signLabel = document.getElementById('sign-label');
            signLabel.getElementsByClassName('sign-status')[0].innerText = '';
        });
        </script>
    """

    @staticmethod
    def account_in(name):
        return """
        <script>
        Jax.ready(function(){
            var signLabel = document.getElementById('sign-label');
            signLabel.getElementsByClassName('sign-status')[0].innerText = '%s';
        });
        </script>
        """ % name