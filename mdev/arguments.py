import argparse

from mdev.commands.add import arguments as add_args
from mdev.commands.disable import arguments as disable_args
from mdev.commands.enable import arguments as enable_args
from mdev.commands.give import arguments as give_args
from mdev.commands.history import arguments as history_args
from mdev.commands.import_ import arguments as import_args
from mdev.commands.make import arguments as make_args
from mdev.commands.run import arguments as run_args
from mdev.commands.script import arguments as script_args

_parser = None


def _get_parser():
    global _parser
    if not _parser:
        _parser = _create_parser()

    return _parser


def _create_parser():
    parser = argparse.ArgumentParser(prog='mdev')
    subparsers = parser.add_subparsers(title="commands", dest="command")

    # add general optionals
    parser.add_argument('--as-user', '-u',
                        type=str,
                        metavar='USER',
                        help="Execute a command as a user. (The default user is set in the mdev.properties file). "
                             "Assumes that the password is the same as the username. If it isn't, also supply the "
                             "--with-password argument.")
    parser.add_argument('--with-password', '-p',
                        type=str,
                        metavar='PASSWORD',
                        help="The password to use when logging in. (The default is set in the mdev.properties file)")
    parser.add_argument('--verbose', '-v',
                        action='count',
                        help='Print verbose messages')

    # add sub commands
    import_args(subparsers)
    make_args(subparsers)
    add_args(subparsers)
    give_args(subparsers)
    enable_args(subparsers)
    disable_args(subparsers)
    run_args(subparsers)
    script_args(subparsers)
    history_args(subparsers)

    return parser


def parse_args():
    return _get_parser().parse_args()


def parse_arg_string(argument_string):
    return _get_parser().parse_args(argument_string)
