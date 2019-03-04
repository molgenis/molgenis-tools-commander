from packaging import version as ver

this_version = ver.parse('7.0.0')
registry = dict()


def version(major, minor, patch):
    def getter():
        print("returning impl: {}".format(this_version))

        def wrapper(*args, **kwargs):
            return registry[this_version](*args, **kwargs)

        return wrapper

    def registrar(func):
        print("registering: {}".format(version_))
        registry[ver.parse(version_)] = func

        return getter()

    return registrar


def main():
    do_action()


@version(7, 0, 0)
def do_action():
    print('impl for 7')


@version('8.0.0')
def do_action():
    print('impl for 8')


main()
