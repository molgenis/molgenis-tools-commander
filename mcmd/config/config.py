"""
Provides access to the configuration.
"""

import operator
from functools import reduce
from pathlib import Path

from ruamel.yaml import YAML

import mcmd.utils.errors as errors

_config = None
_properties_file: Path = None


def set_config(config, properties_file):
    """The config module must not have dependencies on other modules in the config package so the necessary information
    should be passed here."""
    global _config
    if _config:
        raise ValueError('config already set')
    _config = config

    global _properties_file
    if _properties_file:
        raise ValueError('properties file already set')
    _properties_file = properties_file

    _persist()


def _persist():
    """Writes the config to disk."""
    YAML().dump(_config, _properties_file)


def get(*args):
    try:
        prop = _config
        for at in list(args):
            prop = prop[at]
        return prop
    except KeyError as e:
        raise errors.ConfigError('missing property: {}'.format(_key_error_string(e)))


def url():
    try:
        return _get_selected_host_auth()['url']
    except KeyError as e:
        raise errors.ConfigError('missing property: {}'.format(_key_error_string(e)))


def username():
    try:
        return _get_selected_host_auth()['username']
    except KeyError as e:
        raise errors.ConfigError('missing property: {}'.format(_key_error_string(e)))


def token():
    return _get_selected_host_auth().get('token', None)


def password():
    return _get_selected_host_auth().get('password', None)


def git_paths():
    root = get('git', 'root')
    if root is None or len(root) == 0:
        return []
    else:
        root_path = Path(root)
        paths = get('git', 'paths')
        return [root_path.joinpath(path) for path in paths]


def has_option(*args):
    try:
        reduce(operator.getitem, list(args), _config)
        return True
    except KeyError:
        return False


def set_host(url_):
    hosts = get('host', 'auth')
    if url_ in [host_['url'] for host_ in hosts]:
        _config['host']['selected'] = url_
    else:
        raise errors.ConfigError("There is no host with url {}".format(url_))

    _persist()


def add_host(url_, name, pw=None):
    auth = {'url': url_,
            'username': name}
    if pw:
        auth['password'] = pw

    _config['host']['auth'].append(auth)
    _persist()


def host_exists(url_):
    return url_ in [auth['url'] for auth in _config['host']['auth']]


def _get_selected_host_auth():
    selected = get('host', 'selected')
    hosts = get('host', 'auth')
    for host_ in hosts:
        if host_['url'] == selected:
            return host_

    raise errors.ConfigError("The selected host doesn't exist.")


def set_token(token_):
    if token_ is None:
        _get_selected_host_auth().pop('token', None)
    else:
        _get_selected_host_auth()['token'] = token_
    _persist()


def _key_error_string(error):
    return str(error).strip("'")
