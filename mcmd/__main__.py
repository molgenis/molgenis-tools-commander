import sys

# !!! DON'T PLACE IMPORT STATEMENTS BEFORE THE VERSION CHECK !!!
MIN_PYTHON = (3, 6)
if sys.version_info < MIN_PYTHON:
    import platform

    sys.exit(
        "Python {}.{} or later is required. You are running Python {}. Please upgrade to a newer version.\n".format(
            MIN_PYTHON[0],
            MIN_PYTHON[1],
            platform.python_version()))

import logging
import signal

from mcmd.core import update_checker, store
from mcmd.core.context.base_context import Context
from mcmd.args.errors import ArgumentSyntaxError
from mcmd.core.context.home_context import HomeContext
from mcmd.args.parser import parse_args
from mcmd.config.loader import load_config
from mcmd.io import io
from mcmd.io.io import set_debug
from mcmd.io.logging import set_level


def main():
    sys.exit(start(sys.argv, HomeContext()))


def start(argv, context: Context):
    with context:
        # setup friendly interrupt message
        signal.signal(signal.SIGINT, interrupt_handler)

        load_config()
        store.load()
        update_checker.check()

        args = _parse_args(argv)

        setattr(args, 'arg_string', ' '.join(argv[1:]))
        set_log_level(args)

        args.func(args)

        return 0


def start_detached(argv, context: Context):
    with context:
        args = _parse_args(argv)
        setattr(args, 'arg_string', ' '.join(argv[1:]))
        args.func(args)
        return 0


def _parse_args(argv):
    try:
        return parse_args(argv[1:])
    except ArgumentSyntaxError as e:
        sys.stderr.write(e.usage)
        sys.stderr.write(str(e))
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
