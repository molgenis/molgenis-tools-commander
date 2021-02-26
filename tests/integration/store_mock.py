from datetime import datetime
from typing import Optional

import attr
from packaging.version import Version


@attr.s(auto_attribs=True)
class _Storage:
    last_version_check: datetime = datetime.now()
    update_available: Optional[Version] = None

    @classmethod
    def save(cls):
        pass


_store = _Storage()


def load_storage():
    pass


def storage():
    return _store
