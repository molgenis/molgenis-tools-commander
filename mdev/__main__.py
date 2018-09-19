import logging
import sys
from pathlib import Path

from mdev.arguments import parse_args, parse_arg_string
from mdev.configuration import load_config
from mdev.logging import set_level

from mdev import history, io
from mdev.utils import MdevError


def main():
    load_config()
    args = parse_args()
    set_log_level(args)

    if args.command == 'run':
        run(args)
    else:
        execute(args, exit_on_error=True, arg_string=' '.join(sys.argv[1:]))


def run(args):
    script = Path(args.script)
    with open(script) as file:
        lines = [line.rstrip('\n') for line in file]

    exit_on_error = not args.ignore_errors

    for line in lines:
        sub_args = parse_arg_string(line.split(' '))
        if sub_args.command == 'run':
            logging.error("Can't use the run command in a script: %s" % line)
            if exit_on_error:
                exit(1)
            else:
                continue

        execute(sub_args, exit_on_error, line)


def execute(args, exit_on_error, arg_string):
    try:
        args.func(args)
    except MdevError as e:
        io.error(str(e))
        if args.write_to_history:
            history.write(arg_string, success=False)
        if exit_on_error:
            exit(1)
    else:
        if args.write_to_history:
            history.write(arg_string, success=True)
        io.succeed()


def set_log_level(args):
    if args.verbose:
        verbosity = int(args.verbose)
        if verbosity > 0:
            set_level(logging.DEBUG)
    else:
        set_level(logging.INFO)


if __name__ == '__main__':
    main()