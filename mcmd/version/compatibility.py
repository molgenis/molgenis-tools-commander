from collections import defaultdict
from distutils.version import StrictVersion
from functools import wraps
from typing import List

from mcmd.version import molgenis_version

_registry = defaultdict(dict)

MIN_VERSION = '7.0.0'


def version(version_):
    def registrar(func):
        @wraps(func)
        def getter():
            def wrapper(*args, **kwargs):
                id_ = _get_func_id(func)
                available_versions = list(_registry[id_].keys())
                v = _get_closest_version(available_versions)
                wanted_func = _registry[_get_func_id(func)][v]
                return wanted_func(*args, **kwargs)

            return wrapper

        func_id = _get_func_id(func)
        _registry[func_id][version_] = func

        return getter()

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
