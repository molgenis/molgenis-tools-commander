import re
from datetime import datetime, timedelta
from typing import Optional

import pkg_resources
import requests
from packaging.version import Version

from mcmd.core.store import storage
from mcmd.io import io


def check():
    current = _current_version()

    if datetime.now() - timedelta(hours=24) > storage().last_version_check:
        latest = _latest_version()

        if latest and latest > current:
            storage().update_available = latest

        storage().last_version_check = datetime.now()

    latest = storage().update_available
    if latest:
        if latest <= current:
            storage().update_available = None
        else:
            io.warn(
                'A new version of MOLGENIS Commander is available: {}! You are using {}.'.format(latest, current))
            io.info("To upgrade, run 'pip install --upgrade molgenis-commander'")

    storage().save()


def _current_version() -> Version:
    return Version(pkg_resources.get_distribution('molgenis-commander').version)


def _latest_version() -> Optional[Version]:
    response = requests.get('https://pypi.org/simple/molgenis-commander/')
    if response.status_code == 200:
        versions = re.findall(r'molgenis-commander-(\d+\.\d+\.\d+)', response.text)
        latest = max(versions, key=lambda v: Version(v))
        return Version(latest)
