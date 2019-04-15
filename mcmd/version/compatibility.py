"""
This module houses the framework for ensuring compatibility over multiple MOLGENIS versions.
"""

from collections import defaultdict
from distutils.version import StrictVersion
from functools import wraps
from typing import List

from mcmd.version import molgenis_version

_registry = defaultdict(dict)
MIN_VERSION = '7.0.0'


def version(version_):
    """
    Version decorator. Switches implementations based on the version of MOLGENIS.

    Usage:
    >>> @version('7.2.0')
    >>> def impl():
    >>>     print('Implementation for 7.2 and up')
    >>>
    >>> @version('8.0.0')
    >>> def impl():
    >>>     print('Implementation for 8.0 and up')

    Methods using this decorator should have the same name and be in a module with the same name.

    MOLGENIS versions lower than MIN_VERSION aren't supported but the chosen implementation will default to the
    closest match.
    """

    def registrar(func):
        """
        Registers all functions with the @version decorator and replaces them with a general getter that will decide at
        runtime which implementation to return.
        """

        @wraps(func)
        def wrapper():
            def getter(*args, **kwargs):
                """Returns the needed implementation based on the MOLGENIS version."""

                id_ = _get_func_id(func)
                available_versions = list(_registry[id_].keys())
                v = _get_closest_version(available_versions)
                wanted_func = _registry[_get_func_id(func)][v]
                return wanted_func(*args, **kwargs)

            return getter

        func_id = _get_func_id(func)
        _registry[func_id][version_] = func

        return wrapper()

    return registrar


def _get_closest_version(versions: List[str]):
    version_ = molgenis_version.get_version_number()
    if version_ in versions:
        return version_
    else:
        versions.append(version_)
        versions = sorted(versions, key=StrictVersion)
        index = versions.index(version_)
        if index == 0:
            return versions[1]
        else:
            return versions[index - 1]


def _get_func_id(func):
    return '{module}.{function}'.format(module=func.__module__.split('.')[-1], function=func.__name__)
