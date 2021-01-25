import pickle
from datetime import datetime
from typing import Optional

import attr
from packaging.version import Version

from mcmd.core.context import context


@attr.s(auto_attribs=True)
class _Storage:
    last_version_check: datetime = datetime.now()
    update_available: Optional[Version] = None

    @classmethod
    def save(cls):
        with context().get_storage_file().open('wb') as f:
            pickle.dump(_store, f)


_store: Optional[_Storage] = None


def load_storage():
    global _store
    if context().get_storage_file().exists():
        with context().get_storage_file().open('rb') as f:
            _store = pickle.load(f)
    else:
        _store = _Storage()


def storage() -> _Storage:
    return _store
