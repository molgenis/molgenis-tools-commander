from collections import deque
from os import path

from mcmd.config.home import get_history_file
from mcmd.utils import McmdError

_USER_HISTORY = get_history_file()

_INDICATOR_SUCCESS = 'v'
_INDICATOR_FAILURE = 'x'


def write(arg_string, success):
    try:
        history = open(_USER_HISTORY, 'a')

        indicator = _INDICATOR_SUCCESS
        if not success:
            indicator = _INDICATOR_FAILURE

        history.write('%s %s\n' % (indicator, arg_string))
    except OSError as e:
        raise McmdError("Error writing to history: %s" % str(e))


def read(num_lines, include_fails):
    lines = deque()

    if not path.isfile(get_history_file()):
        return lines

    try:
        with open(_USER_HISTORY, 'r') as history:
            for line in history:
                line = line.rstrip('\n')

                if line.startswith(_INDICATOR_FAILURE):
                    if include_fails:
                        lines.append((False, line[2:]))
                else:
                    lines.append((True, line[2:]))

                if len(lines) > num_lines:
                    lines.popleft()
    except OSError as e:
        raise McmdError("Error reading from history: %s" % str(e))

    return lines


def clear():
    try:
        open(_USER_HISTORY, 'w').close()
    except OSError as e:
        raise McmdError("Error clearing history: %s" % str(e))
