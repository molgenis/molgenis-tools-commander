import json

import requests

from mcmd import io
from mcmd.config import config

_username = None
_password = None
_token = None
_as_user = False


def get_token():
    global _password
    if not _token:
        if not _password:
            _password = _ask_password()
        login()
    return _token


def login():
    io.debug('Logging in as user {}'.format(_username))
    response = requests.post(config.api('login'),
                             headers={'Content-Type': 'application/json'},
                             data=json.dumps({"username": _username, "password": _password}))
    global _token
    _token = response.json()['token']
    config.set_token(_token)


def _ask_password():
    return io.password(
        'Please enter the password for user {} on {}'.format(_username, config.host('url')))


def set_(username, password=None, token=None, as_user=False):
    global _username, _password, _token, _as_user
    _username = username
    _password = password
    _token = token
    _as_user = as_user
