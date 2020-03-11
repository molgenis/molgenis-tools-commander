from enum import Enum

from mcmd.config import config
from mcmd.core import history
from mcmd.core.errors import McmdError, ScriptError
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

    def wrapper(args, nested=False):
        """
        :param args: the argparse arguments
        :param nested: if this command was started from another command
        :return: a decorated function
        """

        success = True
        try:
            _set_authentication(args)
            func(args)
        except McmdError as error:
            success = False
            if nested:
                # let the encapsulating command deal with the error
                raise error
            else:
                _handle_error(error)
        else:
            io.succeed()
        finally:
            if args.write_to_history:
                history.write(args.arg_string, success=success)

    return wrapper


def _set_authentication(args):
    if args.as_user:
        if args.with_password:
            auth.set_(username=args.as_user, password=args.with_password, as_user=True)
        else:
            auth.set_(username=args.as_user, password=args.as_user, as_user=True)
    else:
        auth.set_(config.username(), config.password(), config.token())


def _handle_error(error):
    io.error(error.message)
    if error.info:
        io.info(error.info)

    if isinstance(error, ScriptError):
        io.info('Script failed at line {}'.format(io.highlight(str(error.line))))

    exit(1)
