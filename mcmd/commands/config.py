import mcmd.config.config as config
from mcmd.commands._registry import arguments
from mcmd.core.command import command, CommandType
from mcmd.core.errors import McmdError
from mcmd.io import io, ask
from mcmd.io.io import highlight


# =========
# Arguments
# =========

@arguments('config', CommandType.META)
def add_arguments(subparsers):
    p_config = subparsers.add_parser('config',
                                     help='change the configuration of MOLGENIS Commander')
    p_config_subparsers = p_config.add_subparsers(dest='type', metavar='')

    p_config_set = p_config_subparsers.add_parser('set',
                                                  help='set values in the configuration file')

    p_config_set_subparsers = p_config_set.add_subparsers(metavar='')
    p_config_set_host = p_config_set_subparsers.add_parser('host',
                                                           help='select a host')
    p_config_set_host.set_defaults(func=config_set_host,
                                   write_to_history=False)
    p_config_set_host.add_argument('url',
                                   nargs='?',
                                   help='the URL of the host (Optional)')
    p_config_set_import_action = p_config_set_subparsers.add_parser('import-action', help='set import action')
    p_config_set_import_action.set_defaults(func=config_set_import_action, write_to_history=False)

    p_config_add = p_config_subparsers.add_parser('add',
                                                  help='add values in the configuration file')
    p_config_add_subparsers = p_config_add.add_subparsers(metavar='')
    p_config_add_host = p_config_add_subparsers.add_parser('host',
                                                           help='add a new host')
    p_config_add_host.set_defaults(func=config_add_host,
                                   write_to_history=False)


# =======
# Methods
# =======

@command
def config_set_host(args):
    if args.url:
        url = args.url
    else:
        auths = config.get('host', 'auth')
        urls = [auth['url'] for auth in auths]
        url = ask.multi_choice('Please select a host:', urls)

    io.start("Switching to host {}".format(highlight(url)))
    config.set_host(url)

@command
def config_set_import_action(args):
    options = ['add', 'add_update_existing', 'update']
    action = ask.multi_choice('Pick the lines that will form the script:', options)
    io.start("Setting import action to {}".format(highlight(action)))
    config.set_import_action(action)

# noinspection PyUnusedLocal
@command
def config_add_host(args):
    url = _add_host()
    _switch_to_new_host(url)


def _add_host():
    url = ask.input_("URL", required=True)
    if config.host_exists(url):
        raise McmdError("A host with URL {} already exists.".format(url))

    username = ask.input_("Username (Default: admin)")
    password = ask.password("Password (Leave blank to use command line authentication)")

    username = 'admin' if len(username) == 0 else username
    password = None if len(password) == 0 else password

    io.start("Adding host {}".format(highlight(url)))
    config.add_host(url, username, password)
    io.succeed()
    return url


def _switch_to_new_host(url):
    if ask.confirm("Do you want to switch to the new host?"):
        io.start("Switching to host {}".format(highlight(url)))
        config.set_host(url)
