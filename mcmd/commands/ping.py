from colorama import Fore

import mcmd.config.config as config
from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.core.errors import McmdError
from mcmd.in_out.in_out import highlight
from mcmd.molgenis import version as molgenis_version


# =========
# Arguments
# =========

@arguments('ping')
def add_arguments(subparsers):
    p_make = subparsers.add_parser('ping',
                                   help='ping the selected host')
    p_make.set_defaults(func=ping,
                        write_to_history=False)


# =======
# Methods
# =======

# noinspection PyUnusedLocal
@command
def ping(args):
    host = config.get('host', 'selected')
    user = config.username()
    status = Fore.LIGHTGREEN_EX + 'Online' + Fore.RESET
    try:
        version = molgenis_version.get_version()
    except McmdError:
        status = Fore.LIGHTRED_EX + 'Offline' + Fore.RESET
        version = None

    print('   Host:  ' + highlight(host))
    print(' Status:  ' + status)
    if version:
        print('Version:  ' + highlight(version))
    print('   User:  ' + highlight(user))
