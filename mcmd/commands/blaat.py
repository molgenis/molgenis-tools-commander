from mcmd.command import command
from mcmd.commands._registry import arguments
from mcmd.utils.compatibility import version


@command
def blaat(args):
    do_action()
    print()


@arguments('blaat')
def add_arguments(subparsers):
    p_make = subparsers.add_parser('blaat',
                                   help='Blaat')
    p_make.set_defaults(func=blaat,
                        write_to_history=True)


@version('8.0.0')
def do_action():
    print('impl for 8')
