import re
from datetime import datetime, timedelta
from typing import Optional

import pkg_resources
import requests
from packaging.version import Version
from requests import RequestException

from mcmd.core import store
from mcmd.io import io


def check():
    current = _current_version()

    if datetime.now() - timedelta(hours=24) > store.get_last_version_check():
        latest = _latest_version()

        if latest and latest > current:
            store.set_update_available(latest)

        store.set_last_version_check(datetime.now())

    latest = store.get_update_available()
    if latest:
        if latest <= current:
            store.set_update_available(None)
        else:
            _show_update_message(current, latest)


def _current_version() -> Version:
    return Version(pkg_resources.get_distribution('molgenis-commander').version)


def _latest_version() -> Optional[Version]:
    try:
        response = requests.get('https://pypi.org/simple/molgenis-commander/')

        if response.status_code == 200:
            versions = re.findall(r'molgenis-commander-(\d+\.\d+\.\d+)', response.text)
            latest = max(versions, key=lambda v: Version(v))
            return Version(latest)
    except RequestException:
        return None


def _show_update_message(current: Version, latest: Version):
    io.warn(
        'A new version of MOLGENIS Commander is available: {}! You are using {}.'.format(latest, current))
    io.info("To upgrade, run 'pip install --upgrade molgenis-commander'")
