from collections import defaultdict
from functools import wraps
from typing import List

from packaging import version as version_parser

this_version = '7.0.0'
_registry = defaultdict(dict)


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
    versions.sort(key=lambda s: list(map(int, s.split('.'))))
    for i, v in enumerate(versions):
        if version_parser.parse(this_version) < version_parser.parse(v):
            if i == 0:
                return versions[0]
            else:
                return versions[i - 1]
    else:
        return versions[-1]


def _get_func_id(func):
    return '{module}.{function}'.format(module=func.__module__.split('.')[-1], function=func.__name__)
