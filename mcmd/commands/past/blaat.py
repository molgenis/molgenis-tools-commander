from mcmd.utils.compatibility import version


@version('7.1.1')
def do_action():
    print('impl for 7.1.1')


@version('7.0.0')
def do_action():
    print('impl for 7')


@version('7.1.0')
def do_action():
    print('impl for 7.1')
