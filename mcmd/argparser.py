import argparse
import sys

import pkg_resources

# noinspection PyUnresolvedReferences
from mcmd.commands import *
from mcmd.commands import get_argument_adders

_parser = None


def _get_parser():
    global _parser
    if not _parser:
        _parser = _create_parser()

    return _parser


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
    parser.add_argument('--version',
                        action='version',
                        version='Molgenis Commander {version}'.format(version=_get_version()))

    # get and call each command's argument adder
    for argument_adder in get_argument_adders():
        argument_adder(subparsers)

    return parser


def parse_args(arg_list):
    args = _get_parser().parse_args(arg_list)
    _show_help(args, arg_list)
    return args


def _show_help(args, arg_list):
    if not args.command:
        _print_help()
        exit(1)
    elif _is_intermediate_subcommand(args):
        # we can't access the subparser from here, so we parse the arguments again with the --help flag
        arg_list.append('--help')
        parse_args(arg_list)
        exit(1)


def _print_help():
    _get_parser().print_help(sys.stderr)
    exit(1)


def _get_version():
    return pkg_resources.get_distribution('molgenis-commander').version


def _is_intermediate_subcommand(args):
    """
    Some commands have nested subcommands. These intermediate commands are not executable and don't have a 'func'
    property.

    For example:
    > mcmd add user
    Here, 'add' is the intermediate command.
    """
    return not hasattr(args, 'func')
