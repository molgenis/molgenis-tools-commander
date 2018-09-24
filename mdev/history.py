from collections import deque
from os import path

from mdev.utils import MdevError

_USER_HISTORY_DIR = path.join(path.expanduser('~'), '.mdev')
_USER_HISTORY = path.join(_USER_HISTORY_DIR, 'history.log')


def write(arg_string, success):
    try:
        history = open(_USER_HISTORY, 'a')

        indicator = 'v'
        if not success:
            indicator = 'x'

        history.write('%s %s\n' % (indicator, arg_string))
    except OSError as e:
        raise MdevError("Error writing to history: %s" % str(e))


def read(num_lines):
    lines = deque()

    if not path.isfile(_USER_HISTORY):
        return lines

    try:
        with open(_USER_HISTORY, 'r') as history:
            for line in history:
                lines.append(line.rstrip('\n'))
                if len(lines) > num_lines:
                    lines.popleft()
    except OSError as e:
        raise MdevError("Error reading from history: %s" % str(e))

    return lines


def clear():
    try:
        open(_USER_HISTORY, 'w').close()
    except OSError as e:
        raise MdevError("Error clearing history: %s" % str(e))
