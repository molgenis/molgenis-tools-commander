from mdev import history, io
from mdev.config.struct import get_scripts_folder
from mdev.io import confirm
from mdev.utils import MdevError


def script(args):
    lines = history.read(args.number, args.show_fails)

    options = [line[1] for line in lines]

    commands = io.checkbox('Pick the lines that will form the script:', options)
    file_name = _input_script_name()

    try:
        script_file = open(get_scripts_folder().joinpath(file_name), 'w')
        for command in commands:
            script_file.write(command + '\n')
    except OSError as e:
        raise MdevError("Error writing to script: %s" % str(e))


def _input_script_name():
    file_name = ''
    while not file_name:
        name = io.input_('Supply the name of the script:')
        if get_scripts_folder().joinpath(file_name).exists():
            overwrite = confirm('%s already exists. Overwrite?' % name)
            if overwrite:
                file_name = name
        else:
            file_name = name

    return file_name



