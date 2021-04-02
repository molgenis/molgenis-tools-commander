"""
On-disk memory. Used to store data between separate commander runs.
"""

import pickle
from datetime import datetime
from typing import Optional

from packaging.version import Version

from mcmd.core.context import context
from mcmd.core.errors import McmdError

_store = {
    'last_version_check': datetime.now(),
    'update_available': None
}


def load():
    try:
        if context().get_storage_file().exists():
            with context().get_storage_file().open('rb') as f:
                _store.update(pickle.load(f))
    except (pickle.PickleError, IOError) as e:
        raise McmdError("Unable to read storage from file: {}".format(e.message))


def get_last_version_check() -> datetime:
    return _store['last_version_check']


def set_last_version_check(last_check: datetime):
    _store['last_version_check'] = last_check
    _persist()


def get_update_available() -> Optional[Version]:
    return _store['update_available']


# noinspection PyTypeChecker
def set_update_available(version: Optional[Version]):
    _store['update_available'] = version
    _persist()


def _persist():
    try:
        with context().get_storage_file().open('wb') as f:
            pickle.dump(_store, f)
    except (pickle.PickleError, IOError) as e:
        raise McmdError("Unable to save storage to file: {}".format(e.message))
