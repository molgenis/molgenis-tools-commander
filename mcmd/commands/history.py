from mcmd.commands._registry import arguments
from mcmd.core import history as hist
from mcmd.core.command import command, CommandType
from mcmd.io import io
from mcmd.io.logging import get_logger


# =========
# Arguments
# =========

@arguments('history', CommandType.META)
def add_arguments(subparsers):
    p_history = subparsers.add_parser('history',
                                      help="shows the history of commands that were run")
    p_history.set_defaults(func=history,
                           write_to_history=False)
    p_history.add_argument('--number', '-n',
                           type=int,
                           default=10,
                           help='number of lines of history to show (default: 10)')
    p_history.add_argument('--clear', '-c',
                           action='store_true',
                           help='clears the history')


# =======
# Globals
# =======

log = get_logger()


# =======
# Methods
# =======

@command
def history(args):
    if args.clear:
        io.start('Clearing history')
        hist.clear()
    else:
        lines = hist.read(args.number, include_fails=True)
        if len(lines) == 0:
            log.info('History is empty.')
        for line in lines:
            io.start(line[1])
            if line[0]:
                io.succeed()
            else:
                io.error(None)
