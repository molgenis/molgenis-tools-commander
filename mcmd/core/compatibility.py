"""
This module houses the framework responsible for ensuring compatibility over multiple MOLGENIS versions.
"""

from collections import defaultdict
from functools import wraps
from typing import List

from packaging import version as py_version

from mcmd.core.errors import McmdError
from mcmd.molgenis import version as molgenis_version

MIN_VERSION = '7.0.0'
_registry = defaultdict(dict)


def version(version_: str):
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

    Functions using this decorator should have the same name and be in a module with the same name.

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
        if version_ in _registry[func_id]:
            raise ValueError('Function already registered: {}'.format(func_id))

        _registry[func_id][version_] = func

        return wrapper()

    return registrar


def deprecated(since: str, action: str = 'This feature', info: str = None):
    """
    Deprecation decorator.
    Raises a deprecation error when the MOLGENIS version is equal or higher than the given version.

    Usage:
    >>> @deprecated(since='8.1.0',
    >>>             action='doing something',
    >>>             info='This thing should be done in another way.')
    >>> def do_something():
    >>>     print('do something')
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            mol_version = molgenis_version.get_version_number()
            if py_version.parse(mol_version) >= py_version.parse(since):
                message = '{} is deprecated since MOLGENIS {}. You are using MOLGENIS {}.'.format(action.capitalize(),
                                                                                                  since,
                                                                                                  mol_version)
                if info:
                    raise McmdError(message, info=info)
                else:
                    raise McmdError(message)
            else:
                return func(*args, **kwargs)

        return wrapper

    return decorator


def _get_closest_version(versions: List[str]):
    mol_version = molgenis_version.get_version_number()
    if mol_version in versions:
        return mol_version
    else:
        versions.append(mol_version)
        versions = sorted(versions, key=lambda v: py_version.Version(v))
        index = versions.index(mol_version)
        if index == 0:
            # Molgenis version is lower than lowest implementation available. Default to lowest version possible:
            return versions[1]
        else:
            return versions[index - 1]


def _get_func_id(func):
    return '{module}.{function}'.format(module=func.__module__.split('.')[-1], function=func.__name__)
