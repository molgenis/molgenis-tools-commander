"""
Provides access to the configuration.
"""

import operator
from functools import reduce
from pathlib import Path
from urllib.parse import urljoin

from mcmd.utils import McmdError

_config = None


def set_config(config):
    global _config
    if _config:
        raise ValueError('config already set')

    _config = config


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


def _get_selected_host_auth():
    selected = _config['host']['selected']
    hosts = _config['host']['auth']
    for host in hosts:
        if host['url'] == selected:
            return host

    raise McmdError("The selected host doesn't exist.")
