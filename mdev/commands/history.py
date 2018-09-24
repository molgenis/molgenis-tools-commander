from mdev import history as hist
from mdev import io
from mdev.logging import get_logger

log = get_logger()


def history(args):
    if args.clear:
        io.start('Clearing history')
        hist.clear()
    else:
        lines = hist.read(args.number, include_fails=True)
        if len(lines) == 0:
            log.warn('History is empty.')
        for line in lines:
            io.start(line[1])
            if line[0]:
                io.succeed()
            else:
                io.error(None)
