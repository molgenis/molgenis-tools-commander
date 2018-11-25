from mdev import history, io
from mdev.config.struct import get_scripts_folder
from mdev.io import confirm, highlight
from mdev.logging import get_logger
from mdev.utils import MdevError


# =========
# Arguments
# =========

def arguments(subparsers):
    p_script = subparsers.add_parser('script',
                                     help="Do actions involving scripts.")
    p_script.set_defaults(func=script,
                          write_to_history=False)
    p_script_action = p_script.add_mutually_exclusive_group()
    p_script_action.add_argument('--create',
                                 action='store_true',
                                 help='Create a script from the history. (This is the default action.)')
    p_script_action.add_argument('--list', '-l',
                                 action='store_true',
                                 help='List the stored scripts.')
    p_script_action.add_argument('--remove', '-rm',
                                 metavar='SCRIPT NAME',
                                 nargs=1,
                                 type=str,
                                 help='Remove a script.')
    p_script_action.add_argument('--read',
                                 metavar='SCRIPT NAME',
                                 nargs=1,
                                 type=str,
                                 help='Read the contents of a script.')
    p_script.add_argument('--number', '-n',
                          type=int,
                          default=10,
                          help='Number of lines of history to choose from. Default: 10')
    p_script.add_argument('--show-fails', '-f',
                          action='store_true',
                          help='Also show the failed commands from history. Disabled by default.')


# =======
# Globals
# =======

log = get_logger()


# =======
# Methods
# =======

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
