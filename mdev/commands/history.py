from mdev import history as hist
from mdev import io
from mdev.logging import get_logger

log = get_logger()


def history(args):
    if args.clear:
        io.start('Clearing history')
        hist.clear()
    else:
        lines = hist.read(args.number)
        if len(lines) == 0:
            log.warn('History is empty.')
        for line in lines:
            log.info(line)
