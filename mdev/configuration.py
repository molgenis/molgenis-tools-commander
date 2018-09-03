import shutil
from configparser import ConfigParser
from os import path, makedirs

from mdev.logging import get_logger

log = get_logger()

_INSTALL_DIR = path.dirname(__file__)
_DEFAULT_CONFIG = path.join(_INSTALL_DIR, 'config/defaults.ini')
_USER_CONFIG_DIR = path.join(path.expanduser('~'), '.mdev')
_USER_CONFIG = path.join(_USER_CONFIG_DIR, 'mdev.ini')

_config = ConfigParser()


def _create_user_config():
    try:
        makedirs(_USER_CONFIG_DIR, exist_ok=True)
        shutil.copyfile(_DEFAULT_CONFIG, _USER_CONFIG)
    except OSError as err:
        log.error("Error setting up user configuration: %s", err.strerror)
        exit(1)


def _check_user_config():
    if not path.isfile(_USER_CONFIG):
        log.warn("No user configuration file found. Creating it now...")
        _create_user_config()


def load_config():
    _check_user_config()
    _config.read(_USER_CONFIG)


def get_config():
    return _config
