import argparse

import pkg_resources

from mcmd.args._formatter import GroupedHelpFormatter, list_subcommands_in_help
# noinspection PyUnresolvedReferences
# Import all commands:
from mcmd.commands import *
from mcmd.commands import get_argument_adders
from mcmd.core.command import CommandType


# noinspection PyProtectedMember
def create_parser():
    parser = argparse.ArgumentParser(prog='mcmd',
                                     usage=argparse.SUPPRESS,
                                     formatter_class=GroupedHelpFormatter,
                                     description=_description())
    subparsers = parser.add_subparsers(dest="command",
                                       metavar=""  # metavar is empty to hide the {add, delete, disable...} string
                                       )

    # add general optionals
    parser.add_argument('--verbose', '-v',
                        action='count',
                        help='print verbose messages')
    parser.add_argument('--version',
                        action='version',
                        version='Molgenis Commander {version}'.format(version=_get_version()))

    # Remove the 'commands' section title because we will be replacing it
    parser._positionals.title = None

    # add each command's arguments
    for type_ in CommandType:
        for argument_adder in get_argument_adders(type_):
            argument_adder(subparsers)

    # add each command's subcommands to its help string
    list_subcommands_in_help(parser)

    return parser


def _description():
    description = '''\
               _             _                     
     _____ ___| |___ ___ ___|_|___                 
    |     | . | | . | -_|   | |_ -|                
    |_|_|_|___|_|_  |___|_|_|_|___|      _         
           ___ _|___|___ _____ ___ ___ _| |___ ___ 
          |  _| . |     |     | .'|   | . | -_|  _|
          |___|___|_|_|_|_|_|_|__,|_|_|___|___|_|     v{}     


To read more about a (sub)command, run the command with the -h flag (for example: 'mcmd add -h', \
or 'mcmd add group -h').'''.format(_get_version())

    return description


def _get_version():
    return pkg_resources.get_distribution('molgenis-commander').version