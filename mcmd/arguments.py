import argparse
import sys

_parser = None
# _REGISTERED_COMMANDS = list()
_REGISTERED_COMMANDS = dict()


def _get_parser():
    global _parser
    if not _parser:
        _parser = _create_parser()

    return _parser


def arguments(command_name):
    """Command argument registration decorator."""

    def decorator(func):
        _REGISTERED_COMMANDS[command_name] = func
        return func

    return decorator


def _create_parser():
    parser = argparse.ArgumentParser(prog='mcmd')
    subparsers = parser.add_subparsers(title="commands", dest="command")

    # add general optionals
    parser.add_argument('--as-user', '-u',
                        type=str,
                        metavar='USER',
                        help="Execute a command as a user. (The default user is set in the mcmd.properties file). "
                             "Assumes that the password is the same as the username. If it isn't, also supply the "
                             "--with-password argument.")
    parser.add_argument('--with-password', '-p',
                        type=str,
                        metavar='PASSWORD',
                        help="The password to use when logging in. (The default is set in the mcmd.properties file)")
    parser.add_argument('--verbose', '-v',
                        action='count',
                        help='Print verbose messages')

    # add the parser arguments for each command
    for command_name in sorted(_REGISTERED_COMMANDS.keys()):
        _REGISTERED_COMMANDS[command_name](subparsers)

    return parser


def parse_args(arg_list):
    return _get_parser().parse_args(arg_list)


def print_help():
    _get_parser().print_help(sys.stderr)
    exit(1)


def is_intermediate_subcommand(args):
    """
    Some commands have nested subcommands. These intermediate commands are not executable and don't have a 'func'
    property.

    For example:
    > mcmd add user
    Here, 'add' is the intermediate command.
    """
    return not hasattr(args, 'func')


# noinspection PyUnresolvedReferences
from mcmd.commands import *
