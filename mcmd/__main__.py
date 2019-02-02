import logging
import signal
import sys

from mcmd import io
from mcmd.arguments import parse_args, print_help_and_exit, is_intermediate_subcommand
from mcmd.commands.run import run
from mcmd.config.loader import load_config
from mcmd.executor import execute
from mcmd.io import set_debug
from mcmd.logging import set_level


def main():
    # setup friendly interrupt message
    signal.signal(signal.SIGINT, interrupt_handler)

    load_config()

    args = parse_args()
    show_help(args)

    setattr(args, 'arg_string', ' '.join(sys.argv[1:]))
    set_log_level(args)

    if args.command == 'run':
        run(args)
    else:
        execute(args)


def show_help(args):
    if not args.command:
        print_help_and_exit()
    elif is_intermediate_subcommand(args):
        # we can't access the subparser from here, so we parse the arguments again with the --help flag
        sys.argv.append('--help')
        parse_args()
        exit(1)


def set_log_level(args):
    if args.verbose:
        verbosity = int(args.verbose)
        if verbosity > 0:
            set_level(logging.DEBUG)
            set_debug()
    else:
        set_level(logging.INFO)


# noinspection PyUnusedLocal
def interrupt_handler(sig, frame):
    io.warn('Interrupted by user.')
    sys.exit(0)


if __name__ == '__main__':
    main()
