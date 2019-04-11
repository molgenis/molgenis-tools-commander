from mcmd.command import command
from mcmd.commands._registry import arguments
from mcmd.utils import compatibility
from mcmd.utils.compatibility import version


@arguments('blaat')
def add_arguments(subparsers):
    p_make = subparsers.add_parser('blaat',
                                   help='Blaat')
    p_make.set_defaults(func=blaat,
                        write_to_history=True)


@command
def blaat(args):
    do_action()
    print()
    print(compatibility.registry)


@version('8.0.0')
def do_action():
    print('impl for 8')
