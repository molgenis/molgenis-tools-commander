import logging

from mdev.arguments import parse_args
from mdev.configuration import load_config
from mdev.logging import set_level


def main():
    load_config()
    args = parse_args()
    set_log_level(args)
    args.func(args)


def set_log_level(args):
    if args.verbose:
        verbosity = int(args.verbose)
        if verbosity > 0:
            set_level(logging.DEBUG)
    else:
        set_level(logging.INFO)


if __name__ == '__main__':
    main()
