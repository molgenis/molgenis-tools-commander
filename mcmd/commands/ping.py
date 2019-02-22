from colorama import Fore

import mcmd.config.config as config
from mcmd.client.molgenis_client import get_version
from mcmd.io import highlight
from mcmd.utils.errors import McmdError


# =========
# Arguments
# =========

def arguments(subparsers):
    p_make = subparsers.add_parser('ping',
                                   help='Pings the selected host')
    p_make.set_defaults(func=ping,
                        write_to_history=False)


# =======
# Methods
# =======

# noinspection PyUnusedLocal
def ping(args):
    host = config.get('host', 'selected')
    user = config.username()
    status = Fore.LIGHTGREEN_EX + 'Online' + Fore.RESET
    try:
        version = get_version().json()['molgenisVersion']
    except McmdError:
        status = Fore.LIGHTRED_EX + 'Offline' + Fore.RESET
        version = None

    print('   Host:  ' + highlight(host))
    print(' Status:  ' + status)
    if version:
        print('Version:  ' + highlight(version))
    print('   User:  ' + highlight(user))
