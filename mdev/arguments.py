import argparse
from .commands import import_, run, add, make

def parse_args():
    parser = argparse.ArgumentParser(prog='mdev')
    subparsers = parser.add_subparsers(title="commands", dest="command")

    # global optionals
    parser.add_argument('--as-user', '-u',
                        default='admin',
                        nargs='?',
                        help='execute a command as a user (default: admin)')

    # create the parser for the "import" command
    p_import = subparsers.add_parser('import', help='import a file')
    p_import.set_defaults(func=import_)
    p_import.add_argument('file',
                          help='the file to upload')
    p_import.add_argument('--wait', '-w',
                          action='store_true',
                          help='wait for the import to finish before returning')

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
    p_make.set_defaults(func=add)
    p_add.add_argument('type',
                       choices=['group', 'user', 'token'])
    p_add.add_argument('value',
                       type=str,
                       help='the group name, user name or user token to add')

    # create the parser for the "run" command
    p_run = subparsers.add_parser('run', help='run an mdev script')
    p_run.set_defaults(func=run)

    return parser.parse_args()
