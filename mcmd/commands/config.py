import textwrap
from argparse import RawDescriptionHelpFormatter
from pathlib import Path

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
    config_ = subparsers.add_parser('config',
                                    help='change the configuration of MOLGENIS Commander',
                                    formatter_class=RawDescriptionHelpFormatter,
                                    description=textwrap.dedent(
                                        """
                                        Changes values in the configuration file.
                                        
                                        More information about the configuration file can be found on
                                        https://github.com/molgenis/molgenis-tools-commander/wiki/Getting-started 

                                        example usage:
                                          # Adding a host interactively or with arguments
                                          mcmd config add host
                                          mcmd config add host --url http://x --username admin --password admin --switch

                                          # Switching to another host interactively or with arguments
                                          mcmd config set host
                                          mcmd config set host http://localhost 
                                          
                                          # Adding dataset and resource folders
                                          mcmd config add dataset-folder /my/dataset/folder
                                          mcmd config add resource-folder /my/resource/folder

                                          # Enabling and disabling non-interactive mode
                                          mcmd config set non-interactive
                                          mcmd config set interactive

                                          # Setting the default import action interactively and with arguments
                                          mcmd config set import-action
                                          mcmd config set import-action --action add_update_existing
                                        """
                                    ))
    subparsers = config_.add_subparsers(dest='type', metavar='')

    set_ = subparsers.add_parser('set',
                                 help='set values in the configuration file')

    set_subparsers = set_.add_subparsers(metavar='')
    set_host = set_subparsers.add_parser('host',
                                         help='select a host')
    set_host.set_defaults(func=config_set_host,
                          write_to_history=False)
    set_host.add_argument('url',
                          nargs='?',
                          help='the URL of the host (Optional)')

    set_import_action = set_subparsers.add_parser('import-action',
                                                  help='set the default import action')
    set_import_action.set_defaults(func=config_set_import_action, write_to_history=False)
    set_import_action.add_argument('--action',
                                   help='the action to set',
                                   choices=['add', 'add_update_existing', 'update'])

    set_non_interactive = set_subparsers.add_parser('non-interactive',
                                                    help='set non-interactive mode to true')
    set_non_interactive.set_defaults(func=config_set_non_interactive, write_to_history=False)

    set_interactive = set_subparsers.add_parser('interactive',
                                                help='set non-interactive mode to false ')
    set_interactive.set_defaults(func=config_set_interactive, write_to_history=False)

    add = subparsers.add_parser('add',
                                help='add values in the configuration file')
    add_subparsers = add.add_subparsers(metavar='')

    add_host = add_subparsers.add_parser('host',
                                         help='add a new host')
    add_host.set_defaults(func=config_add_host,
                          write_to_history=False)
    add_host.add_argument('--url',
                          help='the URL of the host')
    add_host.add_argument('--username',
                          help='the username of the admin account')
    add_host.add_argument('--password',
                          help='the password of the admin account')
    add_host.add_argument('--switch',
                          action='store_true',
                          help='switch to this new host')

    add_dataset_folder = add_subparsers.add_parser('dataset-folder',
                                                   help='add a dataset folder (datasets are files importable by the '
                                                        'MOLGENIS importer')
    add_dataset_folder.set_defaults(func=config_add_dataset_folder,
                                    write_to_history=False)
    add_dataset_folder.add_argument('folder',
                                    help='the dataset folder to add')

    add_resource_folder = add_subparsers.add_parser('resource-folder',
                                                    help='add a resource folder (resources are files other than '
                                                         'datasets)')
    add_resource_folder.set_defaults(func=config_add_resource_folder,
                                     write_to_history=False)
    add_resource_folder.add_argument('folder',
                                     help='the resource folder to add')


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

    if config.host_exists(url):
        config.set_host(url)
    else:
        raise McmdError("There is no host {} in the config file".format(url))


# noinspection PyUnusedLocal
@command
def config_set_import_action(args):
    if args.action:
        action = args.action
    else:
        options = ['add', 'add_update_existing', 'update']
        action = ask.multi_choice('Choose the default import action:', options)

    io.start("Setting import action to {}".format(highlight(action)))
    config.set_import_action(action)


# noinspection PyUnusedLocal
@command
def config_set_non_interactive(args):
    io.start('Switching to non-interactive mode')
    config.set_non_interactive(True)


# noinspection PyUnusedLocal
@command
def config_set_interactive(args):
    io.start('Switching to interactive mode')
    config.set_non_interactive(False)


# noinspection PyUnusedLocal
@command
def config_add_host(args):
    if args.url:
        url = args.url
    else:
        url = ask.input_("URL", required=True)

    if config.host_exists(url):
        raise McmdError("A host with URL {} already exists.".format(url))

    if args.username:
        username = args.username
    else:
        username = ask.input_("Username (Default: admin)")
        username = 'admin' if len(username) == 0 else username

    if args.password:
        password = args.password
    else:
        password = ask.password("Password (Leave blank to use command line authentication)")
        password = None if len(password) == 0 else password

    io.start("Adding host {}".format(highlight(url)))
    config.add_host(url, username, password)
    io.succeed()

    if args.switch:
        _switch_to_new_host(url)
    elif not config.get('settings', 'non_interactive'):
        if ask.confirm("Do you want to switch to the new host?"):
            _switch_to_new_host(url)


@command
def config_add_dataset_folder(args):
    io.start('Adding resource folder {}'.format(highlight(args.folder)))
    if not Path(args.folder).is_dir():
        raise McmdError('Folder does not exist: {}'.format(args.folder))
    config.add_dataset_folder(args.folder)


@command
def config_add_resource_folder(args):
    io.start('Adding resource folder {}'.format(highlight(args.folder)))
    if not Path(args.folder).is_dir():
        raise McmdError('Folder does not exist: {}'.format(args.folder))
    config.add_resource_folder(args.folder)


def _switch_to_new_host(url):
    io.start("Switching to host {}".format(highlight(url)))
    config.set_host(url)
    io.succeed()
