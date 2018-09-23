from mdev import history as hist
from mdev import io


def history(args):
    if args.clear:
        io.start('Clearing history')
        hist.clear()
    else:
        lines = hist.read(args.number)
        if len(lines) == 0:
            io.warn('History is empty.')
        for line in lines:
            io.info(line)
