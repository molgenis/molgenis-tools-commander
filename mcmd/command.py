from mcmd import history, io
from mcmd.client import auth
from mcmd.config import config
from mcmd.utils.errors import McmdError


def command(func):
    """Decorator for commands. Handles auxiliary actions: authentication, history and errors."""

    def wrapper(args, exit_on_error=True):
        try:
            _set_authentication(args)
            func(args)
        except McmdError as e:
            _handle_error(str(e), args.write_to_history, args.arg_string, exit_on_error)
        else:
            if args.write_to_history:
                history.write(args.arg_string, success=True)
            io.succeed()

    return wrapper


def _set_authentication(args):
    if args.as_user:
        if args.with_password:
            auth.set_(username=args.as_user, password=args.with_password, as_user=True)
        else:
            auth.set_(username=args.as_user, password=args.as_user, as_user=True)
    else:
        auth.set_(config.username(), config.password(), config.token())


def _handle_error(message, write_to_history, arg_string, exit_on_error):
    io.error(message)
    if write_to_history:
        history.write(arg_string, success=False)
    if exit_on_error:
        exit(1)
