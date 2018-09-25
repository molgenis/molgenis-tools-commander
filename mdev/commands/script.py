from os import path, makedirs
from os.path import join

from mdev import history, io
from mdev.io import confirm
from mdev.utils import MdevError

_USER_SCRIPTS_DIR = path.join(path.expanduser('~'), '.mdev/scripts')


def script(args):
    lines = history.read(args.number, args.show_fails)

    options = [line[1] for line in lines]

    file_name = _input_script_name()
    commands = io.checkbox('Pick the lines that will form the script:', options)

    try:
        script_file = open(join(_USER_SCRIPTS_DIR, file_name + '.mdev'), 'w')
        for command in commands:
            script_file.write(command + '\n')
    except OSError as e:
        raise MdevError("Error writing to script: %s" % str(e))


def _input_script_name():
    makedirs(_USER_SCRIPTS_DIR, exist_ok=True)

    file_name = None
    while not file_name:
        name = io.input_('Supply the name of the script:')
        if path.isfile(join(_USER_SCRIPTS_DIR, name + '.mdev')):
            overwrite = confirm('%s.mdev already exists. Overwrite?' % name)
            if overwrite:
                file_name = name
        else:
            file_name = name

    return file_name



