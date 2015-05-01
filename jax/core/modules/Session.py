"""
Created on Jan 30, 2014

@author: Sean Mead
"""

import uuid
import json
import time
import os

from jax.core.modules.Settings import Config


class Static(type):
    SESSIONS = {}


SESSION = 'SESSION'
CACHE = '%ssessions.json' % Config.CACHE_DIR
TIMEOUT = Config.get('session_timeout')
TIMEOUT = TIMEOUT if TIMEOUT else 1440


def save():
    with open(CACHE, 'w') as o:
        json.dump(Static.SESSIONS, o)


def resume():
    try:
        with open(CACHE, 'r') as o:
            Static.SESSIONS = json.load(o)
    except Exception:
        save()


def get_time():
    return int(time.time() / 60)


def start(handler, name):
    sid = str(uuid.uuid4())
    expire = time.time() + TIMEOUT
    handler.set_cookie(name=SESSION, value=sid, expire_epoch=expire)
    Static.SESSIONS[sid] = [name, expire]


def stop(handler):
    if valid(handler):
        Static.SESSIONS.pop(handler.get_cookie(SESSION))


def valid(handler):
    return handler.get_cookie(SESSION) in Static.SESSIONS


def get_name(handler):
    if valid(handler):
        return Static.SESSIONS.get(handler.get_cookie(SESSION))[0]
    return None


if not os.path.isdir(Config.CACHE_DIR):
    os.mkdir(Config.CACHE_DIR)
