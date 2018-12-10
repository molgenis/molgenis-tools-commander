import shutil
from configparser import ConfigParser
from pathlib import Path

from mdev import io
from mdev.config.home import get_properties_file

_INSTALL_DIR = Path(__file__)
_DEFAULT_CONFIG = _INSTALL_DIR.parents[0].joinpath('default.properties')

_config = None


def _create_user_config():
    try:
        shutil.copyfile(_DEFAULT_CONFIG, get_properties_file())
    except OSError as err:
        io.error("Error setting up user configuration: %s" % err.strerror)
        exit(1)


def _check_user_config():
    if not get_properties_file().exists():
        io.info("No properties file found. Creating it now.")
        _create_user_config()


def _load_config():
    global _config
    _check_user_config()
    _config = ConfigParser()
    _config.read(get_properties_file())


def config():
    if not _config:
        _load_config()
    return _config
