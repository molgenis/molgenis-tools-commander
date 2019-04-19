"""
Handles the authentication and provides the REST token to the rest of the application. If a token was
invalidated or simply not present it tries to login with the provided credentials.
"""

import json
from urllib.parse import urljoin

import requests
from requests import HTTPError

from mcmd.io import io
from mcmd.molgenis import api
from mcmd.config import config
from mcmd.core.errors import McmdError, MolgenisOfflineError

_username = None
_password = None
_token = None
_as_user = False


def get_token():
    if not _token:
        _login()
    return _token


def set_(username, password=None, token=None, as_user=False):
    global _username, _password, _token, _as_user
    _username = username
    _password = password
    _token = token
    _as_user = as_user


def check_token():
    """Queries the Token table to see if the set token is valid. The Token table is an arbitrary choice but will work
    because it should always be accessible to the superuser exclusively."""
    if _as_user:
        return

    try:
        response = requests.get(urljoin(api.rest2(), 'sys_sec_Token?q=token=={}'.format(_token)),
                                headers={'Content-Type': 'application/json', 'x-molgenis-token': _token})
        response.raise_for_status()
    except HTTPError as e:
        if e.response.status_code == 401:
            _login()
        else:
            raise McmdError(str(e))
    except requests.exceptions.ConnectionError:
        raise MolgenisOfflineError()


def _login():
    """Logs in with the provided credentials. Prompts the user for a password if no password is found in the config."""
    global _password, _token

    if not _password:
        _password = _ask_password()

    try:
        io.debug('Logging in as user {}'.format(_username))
        response = requests.post(api.login(),
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
        'Please enter the password for user {} on {}'.format(_username, config.url()))
