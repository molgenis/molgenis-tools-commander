import os
import shutil
from pathlib import Path

from mcmd.config import config
from mcmd.core.errors import McmdError


def get_path():
    return Path(config.get('local', 'minio_data'))


def is_empty():
    try:
        path = get_path()
        if not path.exists() or len(os.listdir(path)) == 0:
            return True
        else:
            return False
    except OSError as e:
        raise McmdError('Error reading MinIO data folder: {}'.format(e))


def drop():
    try:
        path = get_path()
        if get_path().exists():
            shutil.rmtree(path)
    except Exception as e:
        raise McmdError('Error dropping {}: {}'.format('MinIO data', e))
