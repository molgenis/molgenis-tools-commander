from mcmd import history as hist
from mcmd import io
from mcmd.logging import get_logger


# =========
# Arguments
# =========

def arguments(subparsers):
    p_history = subparsers.add_parser('history',
                                      help="Shows the history of commands that were run. Commands from scripts are"
                                           " also included.")
    p_history.set_defaults(func=history,
                           write_to_history=False)
    p_history.add_argument('--number', '-n',
                           type=int,
                           default=10,
                           help='Number of lines of history to show. Default: 10')
    p_history.add_argument('--clear', '-c',
                           action='store_true',
                           help='Clears the history.')


# =======
# Globals
# =======

log = get_logger()


# =======
# Methods
# =======

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
