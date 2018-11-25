import logging
import signal
import sys

from mdev import io
from mdev.arguments import parse_args
from mdev.commands.run import run
from mdev.executor import execute
from mdev.io import set_debug
from mdev.logging import set_level


def main():
    # setup friendly interrupt message
    signal.signal(signal.SIGINT, interrupt_handler)

    # show help when no arguments are supplied
    if len(sys.argv) == 1:
        sys.argv.append('--help')

    args = parse_args()
    set_log_level(args)

    if args.command == 'run':
        run(args)
    else:
        execute(args, exit_on_error=True, arg_string=' '.join(sys.argv[1:]))


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
