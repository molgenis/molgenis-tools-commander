import mcmd.io.ask
from mcmd.commands._registry import arguments
from mcmd.core import history
from mcmd.core.command import command, CommandType
from mcmd.core.errors import McmdError
from mcmd.core import context
from mcmd.io import io
from mcmd.io.io import highlight
from mcmd.io.ask import confirm
from mcmd.io.logging import get_logger


# =========
# Arguments
# =========

@arguments('script', CommandType.META)
def add_arguments(subparsers):
    p_script = subparsers.add_parser('script',
                                     help="do actions involving scripts")
    p_script.set_defaults(func=script,
                          write_to_history=False)
    p_script_action = p_script.add_mutually_exclusive_group()
    p_script_action.add_argument('--create',
                                 action='store_true',
                                 help='create a script from the history (this is the default action)')
    p_script_action.add_argument('--list', '-l',
                                 action='store_true',
                                 help='list the stored scripts')
    p_script_action.add_argument('--delete', '-D',
                                 metavar='SCRIPT NAME',
                                 type=str,
                                 help='remove a script')
    p_script_action.add_argument('--read', '-r',
                                 metavar='SCRIPT NAME',
                                 type=str,
                                 help='read the contents of a script')
    p_script.add_argument('--number', '-n',
                          type=int,
                          default=10,
                          help='number of lines of history to choose from (default: 10)')
    p_script.add_argument('--show-fails', '-f',
                          action='store_true',
                          help='also show the failed commands from history (disabled by default)')


# =======
# Globals
# =======

log = get_logger()


# =======
# Methods
# =======

@command
def script(args):
    if args.list:
        _list_scripts()
    elif args.delete:
        _remove_script(args.delete)
    elif args.read:
        _read_script(args.read)
    else:
        _create_script(args)


def _remove_script(script_name):
    path = context().get_scripts_folder().joinpath(script_name)
    _check_script_exists(path)
    try:
        io.start('Removing script %s' % highlight(script_name))
        path.unlink()
    except OSError as e:
        raise McmdError('Error removing script: %s' % str(e))


def _read_script(script_name):
    path = context().get_scripts_folder().joinpath(script_name)
    _check_script_exists(path)
    try:
        with path.open() as f:
            for line in f.readlines():
                log.info(line.strip())
    except OSError as e:
        raise McmdError('Error reading script: %s' % str(e))


def _list_scripts():
    for path in context().get_scripts_folder().iterdir():
        if not path.name.startswith('.'):
            log.info(path.name)


def _create_script(args):
    lines = history.read(args.number, args.show_fails)
    if len(lines) == 0:
        log.info('History is empty.')
        return

    options = [line[1] for line in lines]
    commands = mcmd.io.ask.checkbox('Pick the lines that will form the script:', options)
    file_name = _input_script_name()
    try:
        with context().get_scripts_folder().joinpath(file_name).open('w') as script_file:
            for cmd in commands:
                script_file.write(cmd + '\n')
    except OSError as e:
        raise McmdError("Error writing to script: %s" % str(e))


def _check_script_exists(path):
    if not path.exists():
        raise McmdError("Script %s doesn't exist" % path.name)


def _input_script_name():
    file_name = ''
    while not file_name:
        name = mcmd.io.ask.input_('Supply the name of the script:')
        if context().get_scripts_folder().joinpath(name).exists():
            overwrite = confirm('%s already exists. Overwrite?' % name)
            if overwrite:
                file_name = name
        else:
            file_name = name

    return file_name
