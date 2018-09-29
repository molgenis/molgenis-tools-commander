import logging
import signal
import sys

from mdev import io
from mdev.arguments import parse_args
from mdev.commands.run import execute, run
from mdev.config.config import load_config
from mdev.io import set_debug
from mdev.logging import set_level


def main():
    signal.signal(signal.SIGINT, interrupt_handler)

    if len(sys.argv) == 1:
        # no arguments supplied, show help
        sys.argv.append('--help')

    args = parse_args()
    set_log_level(args)
    load_config()

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


def interrupt_handler(sig, frame):
    io.warn('Interrupted by user.')
    sys.exit(0)


if __name__ == '__main__':
    main()
