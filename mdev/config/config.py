import shutil
from configparser import ConfigParser

import pkg_resources

from mdev import io
from mdev.config.home import get_properties_file
from mdev.utils import MdevError

_DEFAULT_PROPERTIES = pkg_resources.resource_stream('mdev.config', 'default.properties')

_config = None


def _create_user_config():
    try:
        with get_properties_file().open('wb') as properties_file:
            shutil.copyfileobj(_DEFAULT_PROPERTIES, properties_file)
    except OSError as err:
        raise MdevError("Error creating properties file: %s" % err)


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
