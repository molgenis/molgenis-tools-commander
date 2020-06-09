from pathlib import Path
from typing import List

from mcmd.args.actions import ParseKeyValue
from mcmd.commands._registry import arguments
from mcmd.core.command import command, CommandType
from mcmd.core.context import context
from mcmd.core.errors import McmdError
from mcmd.io import io
from mcmd.script import script_runner
from mcmd.script.model.script import Script
from mcmd.script.options import ScriptOptions
from mcmd.script.parser import script_parser
from mcmd.script.parser.errors import InvalidScriptError, ScriptValidationError


@arguments('run', CommandType.META)
def add_arguments(subparsers):
    p_run = subparsers.add_parser('run',
                                  help='run a commander script')
    p_run.set_defaults(func=run,
                       write_to_history=False)
    p_run.add_argument('script',
                       type=str,
                       help='a script from the scripts folder or a path to a script (when using --from-path)')
    p_run.add_argument('--ignore-errors', '-i',
                       action='store_true',
                       help='let the script continue when one or more commands throw an error')
    p_run.add_argument('--hide-comments', '-c',
                       action='store_true',
                       help="don't print comments during script execution")
    p_run.add_argument('--from-line', '-l',
                       type=int,
                       default=1,
                       help="the line number to start the script at")
    p_run.add_argument('--from-path', '-p',
                       action='store_true',
                       help="run a script from a path instead of the ~/.mcmd/scripts folder")
    p_run.add_argument('--with-arguments', '-a',
                       metavar="KEY=VALUE",
                       nargs='+',
                       default=dict(),
                       help="list of arguments to pass to the script as key/value pairs",
                       action=ParseKeyValue)
    p_run.add_argument('--dry', '-d',
                       action='store_true',
                       help='runs the script without actually executing any of the commands')


@command
def run(args):
    script_file = _get_script(args)
    lines = _read_script(script_file)

    script = _try_parse_script(lines)

    options = ScriptOptions(arguments=args.with_arguments,
                            dry_run=args.dry,
                            start_at=args.from_line,
                            log_comments=not args.hide_comments,
                            exit_on_error=not args.ignore_errors)
    script_runner.run(script, options)


def _try_parse_script(lines: List[str]) -> Script:
    try:
        return script_parser.parse(lines)
    except InvalidScriptError as e:
        _print_errors_and_exit(e.errors)


def _print_errors_and_exit(errors: List[ScriptValidationError]):
    io.error('The script contains errors')
    io.newline()

    errors.sort(key=lambda e: e.line_number)

    for error in errors:
        print(error.message)
        io.newline()

    exit(1)


def _get_script(args):
    if args.from_path:
        script = Path(args.script)
    else:
        script = context().get_scripts_folder().joinpath(args.script)
    if not script.exists():
        raise McmdError("The script {} doesn't exist".format(script))
    return script


def _read_script(script):
    try:
        with open(script) as file:
            lines = [line.rstrip('\n') for line in file]
    except OSError as e:
        raise McmdError('Error reading script: {}'.format(str(e)))
    return lines
