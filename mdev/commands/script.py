from mdev import history, io
from mdev.config.struct import get_scripts_folder
from mdev.io import confirm, highlight
from mdev.logging import get_logger
from mdev.utils import MdevError

log = get_logger()


def script(args):
    if args.list:
        _list_scripts()
    elif args.remove:
        _remove_script(args.remove[0])
    elif args.read:
        _read_script(args.read[0])
    else:
        _create_script(args)


def _remove_script(script_name):
    path = get_scripts_folder().joinpath(script_name)
    if not path.exists():
        raise MdevError("Script %s doesn't exist" % script_name)
    else:
        try:
            io.start('Removing script %s' % highlight(script_name))
            path.unlink()
        except OSError as e:
            raise MdevError('Error removing script: %s' % str(e))


def _read_script(script_name):
    path = get_scripts_folder().joinpath(script_name)
    if not path.exists():
        raise MdevError("Script %s doesn't exist" % script_name)
    else:
        try:
            with path.open() as f:
                for line in f.readlines():
                    log.info(line.strip())
        except OSError as e:
            raise MdevError('Error reading script: %s' % str(e))


def _list_scripts():
    for path in get_scripts_folder().iterdir():
        if not path.name.startswith('.'):
            log.info(path.name)


def _create_script(args):
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
        if get_scripts_folder().joinpath(name).exists():
            overwrite = confirm('%s already exists. Overwrite?' % name)
            if overwrite:
                file_name = name
        else:
            file_name = name

    return file_name
