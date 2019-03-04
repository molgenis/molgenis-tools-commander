import logging
import signal
import sys

from mcmd import io
from mcmd.arguments import parse_args
from mcmd.config.loader import load_config
from mcmd.io import set_debug
from mcmd.logging import set_level


def main():
    sys.exit(start(sys.argv))


def start(argv):
    # setup friendly interrupt message
    signal.signal(signal.SIGINT, interrupt_handler)

    load_config()

    args = parse_args(argv[1:])

    setattr(args, 'arg_string', ' '.join(argv[1:]))
    set_log_level(args)

    args.func(args)

    return 0


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
