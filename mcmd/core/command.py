from enum import Enum

from mcmd.config import config
from mcmd.core import history
from mcmd.core.errors import McmdError
from mcmd.io import io
from mcmd.molgenis import auth


class CommandType(Enum):
    # Commands that communicate with a running MOLGENIS over HTTP
    STANDARD = 'standard'

    # Commands that communicate with the database, filestore, etc. of a locally installed MOLGENIS
    LOCAL = 'local'

    # Other commands like configuring MCMD, running scripts, seeing the history, etc.
    META = 'meta'


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
