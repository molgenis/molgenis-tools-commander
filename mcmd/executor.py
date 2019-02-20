import configparser

from mcmd import history, io
from mcmd.client import auth
from mcmd.config import config
from mcmd.utils.utils import McmdError


def execute(args, exit_on_error=True):
    try:
        _set_authentication(args)
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


def _set_authentication(args):
    if args.as_user:
        if args.with_password:
            auth.set_(username=args.as_user, password=args.with_password, as_user=True)
        else:
            auth.set_(username=args.as_user, password=args.username, as_user=True)
    else:
        auth.set_(config.host('username'), config.host('password'), config.host('token'))


def _handle_error(message, write_to_history, arg_string, exit_on_error):
    io.error(message)
    if write_to_history:
        history.write(arg_string, success=False)
    if exit_on_error:
        exit(1)
