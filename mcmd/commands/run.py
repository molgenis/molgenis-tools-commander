import shlex

from mcmd import argparser as arg_parser
from mcmd import io
from mcmd.command import command
from mcmd.commands._registry import arguments
from mcmd.config.home import get_scripts_folder
from mcmd.io import bold, dim
from mcmd.logging import get_logger
from mcmd.utils.kbhit import KBHit


# =========
# Arguments
# =========


@arguments('run')
def add_arguments(subparsers):
    p_run = subparsers.add_parser('run',
                                  help='Run an mcmd script')
    p_run.set_defaults(func=run,
                       write_to_history=False)
    p_run.add_argument('script',
                       type=str,
                       help='The script to run')
    p_run.add_argument('--ignore-errors', '-i',
                       action='store_true',
                       help='Let the script continue when one or more commands throw an error')
    p_run.add_argument('--hide-comments', '-c',
                       action='store_true',
                       help="Don't print comments and whitespace during script execution")


# =======
# Globals
# =======

log = get_logger()


# =======
# Methods
# =======

@command
def run(args):
    script = get_scripts_folder().joinpath(args.script)
    lines = _read_script(script)
    _run_script(not args.hide_comments, not args.ignore_errors, lines)


def _run_script(log_comments, exit_on_error, lines):
    for line in lines:
        if _is_comment(line) or _is_empty(line):
            if log_comments:
                _log_comments(line)
        elif _is_script_function(line):
            _do_script_function(line)
        else:
            _run_command(exit_on_error, line)


def _log_comments(line):
    line = line.strip('#').strip()
    if len(line) == 0:
        io.newline()
    else:
        log.info(line)


def _do_script_function(line):
    line_parts = line.strip('$').split()
    function = line_parts[0]
    if function == 'wait':
        _wait(' '.join(line_parts[1:]).strip())
    else:
        io.error("Unknown function '{}', aborting script".format(function))
        exit(1)


def _wait(message):
    text = '{}: {}   {}'.format(bold('Waiting for user'), message, dim('(Press enter to continue)'))
    io.start(text)
    _wait_for_enter()
    io.succeed()


def _run_command(exit_on_error, line):
    sub_args = arg_parser.parse_args(shlex.split(line))
    setattr(sub_args, 'arg_string', line)
    _fail_on_run_command(exit_on_error, sub_args)
    sub_args.func(sub_args, exit_on_error)


def _fail_on_run_command(exit_on_error, sub_args):
    if sub_args.command == 'run':
        if exit_on_error:
            io.error("Can't use the run command in a script: {}".format(sub_args.arg_string))
            exit(1)
        else:
            return


def _read_script(script):
    lines = list()
    try:
        with open(script) as file:
            lines = [line.rstrip('\n') for line in file]
    except OSError as e:
        io.error('Error reading script: {}'.format(str(e)))
    exit(1)
    return lines


def _is_comment(line):
    return line.strip().startswith('#')


def _is_empty(line):
    return line.isspace() or len(line) == 0


def _is_script_function(line):
    return line.startswith('$')


def _wait_for_enter():
    kb = KBHit()
    while True:
        if kb.kbhit():
            c = kb.getch()
            if c == '\n':  # Enter
                break
