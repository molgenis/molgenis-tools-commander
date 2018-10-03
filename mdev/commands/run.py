import configparser
from pathlib import Path

from mdev import io, history
from mdev.arguments import parse_arg_string
from mdev.utils import MdevError


def run(args):
    if not args.script.endswith('.mdev'):
        args.script += '.mdev'

    script = Path().home().joinpath('.mdev', 'scripts', args.script)

    lines = list()
    try:
        with open(script) as file:
            lines = [line.rstrip('\n') for line in file]
    except OSError as e:
        io.error('Error reading script: %s' % str(e))

    exit_on_error = not args.ignore_errors
    for line in lines:
        sub_args = parse_arg_string(line.split(' '))
        if sub_args.command == 'run':
            io.error("Can't use the run command in a script: %s" % line)
            if exit_on_error:
                exit(1)
            else:
                continue

        execute(sub_args, exit_on_error, line)


def execute(args, exit_on_error, arg_string):
    try:
        args.func(args)
    except MdevError as e:
        _handle_error(str(e), args.write_to_history, arg_string, exit_on_error)
    except configparser.Error as e:
        message = 'Error reading or writing mdev.ini: %s' % str(e)
        _handle_error(message, args.write_to_history, arg_string, exit_on_error)
    else:
        if args.write_to_history:
            history.write(arg_string, success=True)
        io.succeed()


def _handle_error(message, write_to_history, arg_string, exit_on_error):
    io.error(message)
    if write_to_history:
        history.write(arg_string, success=False)
    if exit_on_error:
        exit(1)
