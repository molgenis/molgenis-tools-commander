import sys

from mcmd.args import _factory

_parser = None


def _get_parser():
    global _parser
    if not _parser:
        _parser = _factory.create_parser()

    return _parser


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


def _is_intermediate_subcommand(args):
    """
    Some commands have nested subcommands. These intermediate commands are not executable and don't have a 'func'
    property.
    For example:
    > mcmd add user
    Here, 'add' is the intermediate command.
    """
    return not hasattr(args, 'func')
