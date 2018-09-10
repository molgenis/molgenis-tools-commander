import argparse

from .commands import import_, add, make


def _create_parser():
    parser = argparse.ArgumentParser(prog='mdev')
    subparsers = parser.add_subparsers(title="commands", dest="command")

    # global optionals
    parser.add_argument('--as-user', '-u',
                        default='admin',
                        nargs='?',
                        help='execute a command as a user (default: admin)')
    parser.add_argument('--verbose', '-v',
                        action='count',
                        help='print verbose messages')

    # create the parser for the "import" command
    p_import = subparsers.add_parser('import', help='import a file')
    p_import.set_defaults(func=import_)
    p_import.add_argument('file',
                          help='the file to upload')
    p_import_source = p_import.add_mutually_exclusive_group()
    p_import_source.add_argument('--from-path', '-p',
                                 action='store_true',
                                 help='select a file by path instead of by looking in quick folders')

    # create the parser for the "make" command
    p_make = subparsers.add_parser('make', help='make a user member of a role')
    p_make.set_defaults(func=make)
    p_make.add_argument('user',
                        type=str,
                        help='the user to make a member')
    p_make.add_argument('role',
                        type=str,
                        help='the role to make the user a member of')

    # create the parser for the "add" command
    p_add = subparsers.add_parser('add', help='add a user, group or token')
    p_add.set_defaults(func=add)
    p_add.add_argument('type',
                       choices=['group', 'user'])
    p_add.add_argument('value',
                       type=str,
                       help='the group name, user name or user token to add')

    # create the parser for the "run" command
    p_run = subparsers.add_parser('run', help='run an mdev script')
    p_run.add_argument('script',
                       type=str,
                       help='the .mdev script to run')
    p_run.add_argument('--ignore-errors', '-i',
                       action='store_true',
                       help='let the script continue when one or more commands throw an error')
    return parser


_parser = _create_parser()


def parse_args():
    return _parser.parse_args()


def parse_arg_string(argument_string):
    return _parser.parse_args(argument_string)
