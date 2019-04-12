from colorama import Fore

import mcmd.config.config as config
from mcmd.client import api
from mcmd.client.molgenis_client import get_no_login
from mcmd.command import command
from mcmd.commands._registry import arguments
from mcmd.io import highlight
from mcmd.utils.errors import McmdError


# =========
# Arguments
# =========

@arguments('ping')
def add_arguments(subparsers):
    p_make = subparsers.add_parser('ping',
                                   help='Pings the selected host')
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
        version = get_no_login(api.version()).json()['molgenisVersion']
    except McmdError:
        status = Fore.LIGHTRED_EX + 'Offline' + Fore.RESET
        version = None

    print('   Host:  ' + highlight(host))
    print(' Status:  ' + status)
    if version:
        print('Version:  ' + highlight(version))
    print('   User:  ' + highlight(user))
