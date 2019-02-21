"""
Handles the authentication and provides the REST token to the rest of the application. If a token was
invalidated or simply not present it tries to login with the provided credentials.
"""

import json

import requests
from requests import HTTPError

from mcmd import io
from mcmd.config import config
from mcmd.utils.utils import McmdError

_username = None
_password = None
_token = None
_as_user = False


def get_token():
    if not _token:
        _login()
    return _token


def invalidate_token():
    global _token
    _token = None


def set_(username, password=None, token=None, as_user=False):
    global _username, _password, _token, _as_user
    _username = username
    _password = password
    _token = token
    _as_user = as_user


def _login():
    """Logs in with the provided credentials. Prompts the user for a password if no password is found in the config."""
    global _password, _token

    if not _password:
        _password = _ask_password()

    try:
        io.debug('Logging in as user {}'.format(_username))
        response = requests.post(config.api('login'),
                                 headers={'Content-Type': 'application/json'},
                                 data=json.dumps({"username": _username, "password": _password}))
        response.raise_for_status()
        _token = response.json()['token']
    except HTTPError as e:
        if e.response.status_code == 401:
            raise McmdError('Invalid login credentials')
        else:
            raise McmdError(str(e))
    finally:
        if not _as_user:
            config.set_token(_token)


def _ask_password():
    return io.password(
        'Please enter the password for user {} on {}'.format(_username, config.host('url')))
