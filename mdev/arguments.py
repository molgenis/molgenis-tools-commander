import argparse

from .commands import import_, add, make, give, history


def _create_parser():
    parser = argparse.ArgumentParser(prog='mdev')
    subparsers = parser.add_subparsers(title="commands", dest="command")

    # global optionals
    parser.add_argument('--as-user', '--user', '-u',
                        nargs=1,
                        type=str,
                        help="Execute a command as a user. (The default user is set in the mdev.ini file). Assumes "
                             "that the password is the same as the username. If it isn't, also supply the --password "
                             "argument.")
    parser.add_argument('--with-password', '--password', '-p',
                        nargs=1,
                        type=str,
                        help="The password to use when logging in. (The default is set in the mdev.ini file)")
    parser.add_argument('--verbose', '-v',
                        action='count',
                        help='Print verbose messages')

    # create the parser for the "import" command
    p_import = subparsers.add_parser('import',
                                     help='Import a file')
    p_import.set_defaults(func=import_,
                          write_to_history=True)
    p_import.add_argument('file',
                          help='The file to upload')
    p_import_source = p_import.add_mutually_exclusive_group()
    p_import_source.add_argument('--from-path', '-p',
                                 action='store_true',
                                 help='Select a file by path instead of by looking in quick folders')
    p_import_source.add_argument('--from-issue', '-i',
                                 action='store_true',
                                 help='Import a file from a GitHub issue')

    # create the parser for the "make" command
    p_make = subparsers.add_parser('make',
                                   help='Make a user member of a role')
    p_make.set_defaults(func=make,
                        write_to_history=True)
    p_make.add_argument('user',
                        type=str,
                        help='The user to make a member')
    p_make.add_argument('role',
                        type=str,
                        help='The role to make the user a member of')

    # create the parser for the "add" command
    p_add = subparsers.add_parser('add',
                                  help='Add a user, group or token')
    p_add.set_defaults(func=add,
                       write_to_history=True)
    p_add.add_argument('type',
                       choices=['group', 'user'])
    p_add.add_argument('value',
                       type=str,
                       help='The group name, user name or user token to add')

    # create the parser for the "give" command
    p_give = subparsers.add_parser('give',
                                   help='Give permissions on resources to roles or users')
    p_give.set_defaults(func=give,
                        write_to_history=True)
    p_give.add_argument('--user',
                        action='store_true',
                        help='Give the permission to a user instead of a role')
    p_give_resource = p_give.add_mutually_exclusive_group()
    p_give_resource.add_argument('--entity-type', '-e',
                                 action='store_true',
                                 help='Flag to specify that the resource is an entity type')
    p_give_resource.add_argument('--package', '-p',
                                 action='store_true',
                                 help='Flag to specify that the resource is a package')
    p_give_resource.add_argument('--plugin', '-pl',
                                 action='store_true',
                                 help='Flag to specify that the resource is a plugin')
    p_give.add_argument('receiver',
                        type=str,
                        help='The role (or user) to give the permission to')
    p_give.add_argument('permission',
                        choices=['none', 'writemeta', 'readmeta', 'write', 'read', 'count', 'n', 'wm', 'rm', 'w', 'r',
                                 'c'],
                        help='The permission type to give')
    p_give.add_argument('resource',
                        type=str,
                        help='The resource to which permission is given')

    # create the parser for the "run" command
    p_run = subparsers.add_parser('run',
                                  help='Run an mdev script')
    p_run.set_defaults(write_to_history=False)
    p_run.add_argument('script',
                       type=str,
                       help='The .mdev script to run')
    p_run.add_argument('--ignore-errors', '-i',
                       action='store_true',
                       help='Let the script continue when one or more commands throw an error')

    # create the parser for the "history" command
    p_history = subparsers.add_parser('history',
                                      help="Shows the history of commands that were run. Commands from scripts are"
                                           " also included.")
    p_history.set_defaults(func=history,
                           write_to_history=False)
    p_history.add_argument('--number', '-n',
                           type=int,
                           default=10,
                           help='Number of lines of history to show. Default: 20')
    p_history.add_argument('--clear', '-c',
                           action='store_true',
                           help='Clears the history.')
    return parser


_parser = _create_parser()


def parse_args():
    return _parser.parse_args()


def parse_arg_string(argument_string):
    return _parser.parse_args(argument_string)
