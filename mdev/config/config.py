import shutil
from configparser import ConfigParser
from os import path, makedirs

from mdev import io

_INSTALL_DIR = path.dirname(__file__)
_DEFAULT_CONFIG = path.join(_INSTALL_DIR, 'config/defaults.ini')
_USER_CONFIG_DIR = path.join(path.expanduser('~'), '.mdev')
_USER_CONFIG = path.join(_USER_CONFIG_DIR, 'mdev.ini')

_config = None


def _create_user_config():
    try:
        makedirs(_USER_CONFIG_DIR, exist_ok=True)
        shutil.copyfile(_DEFAULT_CONFIG, _USER_CONFIG)
    except OSError as err:
        io.error("Error setting up user configuration: %s" % err.strerror)
        exit(1)


def _check_user_config():
    if not path.isfile(_USER_CONFIG):
        io.info("No user configuration file found. Creating it now.")
        _create_user_config()


def _load_config():
    global _config
    _check_user_config()
    _config = ConfigParser()
    _config.read(_USER_CONFIG)


def config():
    if not _config:
        _load_config()
    return _config
