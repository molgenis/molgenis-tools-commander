import os
import shutil
from pathlib import Path

from mcmd.config import config
from mcmd.core.errors import McmdError


def get_path():
    return Path(config.get('local', 'molgenis_home')).joinpath('data').joinpath('filestore')


def is_empty():
    try:
        path = get_path()
        if not path.exists() or len(os.listdir(path)) == 0:
            return True
        else:
            return False
    except OSError as e:
        raise McmdError('Error reading filestore: {}'.format(e))


def drop():
    try:
        path = get_path()
        if path.exists():
            shutil.rmtree(path)
    except Exception as e:
        raise McmdError('Error dropping {}: {}'.format('filestore', e))
