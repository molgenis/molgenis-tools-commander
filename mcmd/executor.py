import configparser

from mcmd import history, io
from mcmd.utils import McmdError


def execute(args, exit_on_error=True):
    try:
        args.func(args)
    except McmdError as e:
        _handle_error(str(e), args.write_to_history, args.arg_string, exit_on_error)
    except configparser.Error as e:
        message = 'Error reading or writing mcmd.properties: %s' % str(e)
        _handle_error(message, args.write_to_history, args.arg_string, exit_on_error)
    else:
        if args.write_to_history:
            history.write(args.arg_string, success=True)
        io.succeed()


def _handle_error(message, write_to_history, arg_string, exit_on_error):
    io.error(message)
    if write_to_history:
        history.write(arg_string, success=False)
    if exit_on_error:
        exit(1)
