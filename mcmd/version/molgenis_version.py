"""Contains the MOLGENIS version of the current host."""
import re

import requests
from requests import HTTPError

from mcmd.client import api
from mcmd.utils.errors import McmdError, MolgenisOfflineError

_version_number = None
_version = None


def get_version():
    """
    Gets the MOLGENIS version lazily.
    """
    global _version
    if not _version:
        _get_version()
    return _version


def get_version_number():
    """
    Gets the MOLGENIS version lazily and only returns the version number: '8.0.0-SNAPSHOT' will become '8.0.0'
    """
    global _version_number
    if not _version_number:
        _get_version()
    return _version_number


def _get_version():
    try:
        response = requests.get(api.version(),
                                headers={'Content-Type': 'application/json'})
        response.raise_for_status()

        global _version
        global _version_number
        _version = response.json()['molgenisVersion']
        _version_number = _extract_version_number(_version)
    except HTTPError as e:
        raise McmdError(str(e))
    except requests.exceptions.ConnectionError:
        raise MolgenisOfflineError()


def _extract_version_number(_version):
    return re.match(r"\d+.\d+.\d+", _version).group()
