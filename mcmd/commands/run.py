from mcmd import argparser as arg_parser
from mcmd.commands._registry import arguments
from mcmd.command import command
from mcmd.config.home import get_scripts_folder
from mcmd.utils.errors import McmdError


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
                       help='The .mcmd script to run')
    p_run.add_argument('--ignore-errors', '-i',
                       action='store_true',
                       help='Let the script continue when one or more commands throw an error')


# =======
# Methods
# =======

@command
def run(args):
    script = get_scripts_folder().joinpath(args.script)

    try:
        with open(script) as file:
            lines = [line.rstrip('\n') for line in file]
    except OSError as e:
        raise McmdError('Error reading script: {}'.format(str(e)))

    exit_on_error = not args.ignore_errors
    for line in lines:
        sub_args = arg_parser.parse_args(line.split(' '))
        setattr(sub_args, 'arg_string', line)
        if sub_args.command == 'run':
            raise McmdError("Can't use the run command in a script: {}".format(line))

        sub_args.func(sub_args, exit_on_error)
