"""
Provides access to the configuration.
"""

import operator
from functools import reduce
from pathlib import Path
from urllib.parse import urljoin

from ruamel.yaml import YAML

from mcmd.config.home import get_properties_file
from mcmd.utils import McmdError

_config = None


def set_config(config):
    global _config
    if _config:
        raise ValueError('config already set')

    _config = config
    _persist()


def _persist():
    """Writes the config to disk."""
    YAML().dump(_config, get_properties_file())


def get(*args):
    prop = _config
    for at in list(args):
        prop = prop[at]
    return prop


def username():
    return _get_selected_host_auth()['username']


def password():
    return _get_selected_host_auth()['password']


def git_paths():
    root = _config['git']['root']
    if root is None or len(root) == 0:
        return []
    else:
        root_path = Path(root)
        paths = _config['git']['paths']
        return [root_path.joinpath(path) for path in paths]


def api(endpoint):
    """Returns the combination of the host's url and the API endpoint."""
    url = _config['host']['selected']
    return urljoin(url, get('api', endpoint))


def has_option(*args):
    try:
        reduce(operator.getitem, list(args), _config)
        return True
    except KeyError:
        return False


def set_host(url):
    hosts = _config['host']['auth']
    if url in [host['url'] for host in hosts]:
        _config['host']['selected'] = url
    else:
        raise McmdError("There is no host with url {}".format(url))

    _persist()


def add_host(url, name, pw):
    auth = {'url': url,
            'username': name,
            'password': pw}

    _config['host']['auth'].append(auth)
    _persist()


def host_exists(url):
    return url in [auth['url'] for auth in _config['host']['auth']]


def _get_selected_host_auth():
    selected = _config['host']['selected']
    hosts = _config['host']['auth']
    for host in hosts:
        if host['url'] == selected:
            return host

    raise McmdError("The selected host doesn't exist.")
