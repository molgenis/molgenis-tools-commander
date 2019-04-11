from collections import defaultdict
from functools import wraps

this_version = '8.0.0'
print('this version:', this_version)
registry = defaultdict(dict)


def version(version_):
    def registrar(func):
        @wraps(func)
        def getter():
            def wrapper(*args, **kwargs):
                func_id = get_func_id(func)
                impl_versions = list(registry[func_id].keys())
                impl_versions.sort(key=lambda s: list(map(int, s.split('.'))))
                print(impl_versions)

                return registry[get_func_id(func)][this_version](*args, **kwargs)

            return wrapper

        func_id = get_func_id(func)
        print("registering {} {}".format(func_id, version_))
        registry[func_id][version_] = func

        return getter()

    return registrar


def get_func_id(func):
    return '{module}.{function}'.format(module=func.__module__.split('.')[-1], function=func.__name__)
