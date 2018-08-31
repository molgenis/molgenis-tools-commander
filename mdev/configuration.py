import logging
import shutil
from configparser import ConfigParser
from os import path, makedirs

LOG = logging.getLogger()

_INSTALL_DIR = path.dirname(__file__)
_DEFAULT_CONFIG = path.join(_INSTALL_DIR, 'config/defaults.ini')
_USER_CONFIG_DIR = path.join(path.expanduser('~'), '.mdev')
_USER_CONFIG = path.join(_USER_CONFIG_DIR, 'mdev.ini')


def _create_user_config():
    try:
        makedirs(_USER_CONFIG_DIR, exist_ok=True)
        shutil.copyfile(_DEFAULT_CONFIG, _USER_CONFIG)
    except OSError as err:
        LOG.error("Error setting up user configuration: %s", err.strerror)
        exit(1)


def _check_user_config():
    if not path.isfile(_USER_CONFIG):
        LOG.info("No user configuration file found. Creating it now...")
        _create_user_config()


def get_config():
    _check_user_config()
    config = ConfigParser()
    config.read(_USER_CONFIG)
    return config
