import mimetypes
import textwrap
from argparse import RawDescriptionHelpFormatter
from os import path as os_path
from pathlib import Path
from typing import List

from mcmd.commands._registry import arguments
from mcmd.core.context import context
from mcmd.core.command import command
from mcmd.core.compatibility import version
from mcmd.core.errors import McmdError
from mcmd.io import io
from mcmd.io.io import highlight
from mcmd.molgenis import api
from mcmd.molgenis.client import post, get, post_files
from mcmd.molgenis.principals import to_role_name
from mcmd.utils.file_helpers import get_file_name_from_path, scan_folders_for_files, select_path

# Store a reference to the parser so that we can show an error message for the custom validation rule
p_add_theme = None


# =========
# Arguments
# =========

@arguments('add')
def add_arguments(subparsers):
    global p_add_theme
    p_add = subparsers.add_parser('add',
                                  help='add and upload resources',
                                  description="Run 'mcmd add group -h' or 'mcmd add user -h' to view the help for those"
                                              " subcommands")
    p_add_subparsers = p_add.add_subparsers(dest="type", metavar='')

    p_add_group = p_add_subparsers.add_parser('group',
                                              help='add a group')
    p_add_group.set_defaults(func=add_group,
                             write_to_history=True)
    p_add_group.add_argument('name',
                             type=str,
                             help="the group's name")

    p_add_user = p_add_subparsers.add_parser('user',
                                             help='add a user')
    p_add_user.set_defaults(func=add_user,
                            write_to_history=True)
    p_add_user.add_argument('username',
                            type=str,
                            help="the user's name")
    p_add_user.add_argument('--set-password', '-p',
                            metavar='PASSWORD',
                            type=str,
                            help="the user's password")
    p_add_user.add_argument('--with-email', '-e',
                            metavar='EMAIL',
                            type=str,
                            help="the user's e-mail address")
    p_add_user.add_argument('--is-inactive', '-a',
                            action='store_true',
                            help="make user inactive")
    p_add_user.add_argument('--is-superuser', '-s',
                            action='store_true',
                            help="make user superuser")
    p_add_user.add_argument('--change-password', '-c',
                            action='store_true',
                            help="set change password to true for user")

    p_add_role = p_add_subparsers.add_parser('role',
                                             help='add a role',
                                             formatter_class=RawDescriptionHelpFormatter,
                                             description=textwrap.dedent(
                                                 """
                                                 Add a (group) role. 
    
                                                 Note: since MOLGENIS 8.3 role names are case sensitive and need to 
                                                 be typed exactly as-is. (Before 8.3 all role names will be upper 
                                                 cased automatically). 
    
                                                 Example usage:
                                                   mcmd add role COUNTER
                                                   mcmd add role gcc_COUNTER --to-group gcc --includes COUNTER                                      
                                                 """
                                             ))
    p_add_role.set_defaults(func=add_role,
                            write_to_history=True)
    p_add_role.add_argument('rolename',
                            help="the role's name")
    p_add_role.add_argument('--to-group', '-g',
                            dest='group',
                            metavar='GROUP NAME',
                            help='the group to add the role to')
    p_add_role.add_argument('--includes', '-i',
                            metavar='ROLE NAMES',
                            nargs='+',
                            help='the role(s) that this role includes (if more than one, separated by a whitespace)')

    p_add_package = p_add_subparsers.add_parser('package',
                                                help='add a package')
    p_add_package.set_defaults(func=add_package,
                               write_to_history=True)
    p_add_package.add_argument('id',
                               type=str,
                               help="the id of the Package")
    p_add_package.add_argument('--in',
                               type=str,
                               dest='parent',
                               help="the id of the parent")

    p_add_token = p_add_subparsers.add_parser('token',
                                              help='add a token')
    p_add_token.set_defaults(func=add_token,
                             write_to_history=True)
    p_add_token.add_argument('user',
                             type=str,
                             help="the user to give the token to")
    p_add_token.add_argument('token',
                             type=str,
                             help="the token")

    p_add_theme = p_add_subparsers.add_parser('theme',
                                              help='upload a bootstrap theme')
    p_add_theme.set_defaults(func=add_theme,
                             write_to_history=True)
    p_add_theme.add_argument('--from-path', '-p',
                             action='store_true',
                             help='add a bootstrap theme by specifying a path')

    required_named = p_add_theme.add_argument_group('required named arguments')
    required_named.add_argument('--bootstrap3', '-3',
                                type=str,
                                metavar='STYLESHEET',
                                help="the bootstrap3 css theme file (when not specified, the default molgenis theme "
                                     "will be applied on bootstrap3 pages)")

    p_add_theme.add_argument('--bootstrap4', '-4',
                             type=str,
                             metavar='STYLESHEET',
                             help="the bootstrap4 css theme file (when not specified, the default molgenis theme will "
                                  "be applied on bootstrap4 pages)")

    p_add_logo = p_add_subparsers.add_parser('logo',
                                             help='upload a logo to be placed on the left top of the menu')
    p_add_logo.set_defaults(func=add_logo,
                            write_to_history=True)
    p_add_logo.add_argument('--from-path', '-p',
                            action='store_true',
                            help='add a logo by specifying a path')
    p_add_logo.add_argument('logo',
                            type=str,
                            help="the image you want to use as logo")


# =======
# Methods
# =======

@command
def add_user(args):
    io.start('Adding user %s' % highlight(args.username))

    password = args.set_password if args.set_password else args.username
    email = args.with_email if args.with_email else args.username + '@molgenis.org'
    active = not args.is_inactive
    superuser = args.is_superuser
    ch_pwd = args.change_password

    post(api.rest1('sys_sec_User'),
         data={'username': args.username,
               'password_': password,
               'changePassword': ch_pwd,
               'Email': email,
               'active': active,
               'superuser': superuser
               })


@command
def add_role(args):
    role_name = to_role_name(args.rolename)
    io.start('Adding role {}'.format(highlight(role_name)))

    role = {'name': role_name,
            'label': role_name}

    if args.includes:
        role_names = [to_role_name(name) for name in args.includes]
        role['includes'] = _get_role_ids(role_names)

    if args.group:
        group_name = _to_group_name(args.group)
        role['group'] = _get_group_id(group_name)

    data = {'entities': [role]}
    post(api.rest2('sys_sec_Role'), data=data)


def _get_group_id(group_name) -> str:
    groups = get(api.rest2('sys_sec_Group'),
                 params={
                     'attrs': 'id',
                     'q': 'name=={}'.format(group_name)
                 }).json()['items']
    if len(groups) == 0:
        raise McmdError('No group found with name {}'.format(groups))
    else:
        return groups[0]['id']


def _get_role_ids(role_names) -> List[str]:
    roles = get(api.rest2('sys_sec_Role'),
                params={
                    'attrs': 'id,name',
                    'q': 'name=in=({})'.format(','.join(role_names))
                }).json()['items']

    name_to_id = {role['name']: role['id'] for role in roles}
    not_found = list()
    for role_name in role_names:
        if role_name not in name_to_id:
            not_found.append(role_name)

    if len(not_found) > 0:
        raise McmdError("Couldn't find role(s) {}".format(' and '.join(not_found)))
    else:
        return list(name_to_id.values())


@command
def add_group(args):
    group_name = _to_group_name(args.name)
    io.start('Adding group %s' % highlight(group_name))
    post(api.group(), data={'name': group_name, 'label': args.name})


@version('7.0.0')
def _to_group_name(group_input: str):
    """Before 8.3.0 all group names are lower case."""
    return group_input.lower()


@version('8.3.0')
def _to_group_name(group_input: str):
    """Since 8.3.0 group names are case sensitive."""
    return group_input


@command
def add_package(args):
    io.start('Adding package %s' % highlight(args.id))

    data = {'id': args.id,
            'label': args.id}

    if args.parent:
        data['parent'] = args.parent

    post(api.rest1('sys_md_Package'), data=data)


@command
def add_token(args):
    io.start('Adding token %s for user %s' % (highlight(args.token), highlight(args.user)))

    user = get(api.rest2('sys_sec_User'),
               params={
                   'attrs': 'id',
                   'q': 'username=={}'.format(args.user)
               })
    if user.json()['total'] == 0:
        raise McmdError('Unknown user %s' % args.user)

    user_id = user.json()['items'][0]['id']

    data = {'User': user_id,
            'token': args.token}

    post(api.rest1('sys_sec_Token'), data=data)


@command
def add_theme(args):
    """
    add_theme adds a theme to the stylesheet table
    :param args: commandline arguments containing bootstrap3_theme and optionally bootstrap4_theme
    :return: None
    """
    _validate_args(args)
    valid_types = {'text/css'}
    api_ = api.add_theme()
    bs3_name = args.bootstrap3
    bs4 = args.bootstrap4
    paths = [bs3_name]
    names = ['bootstrap3-style']
    if bs4:
        paths.append(bs4)
        names.append('bootstrap4-style')
        bs4_name = get_file_name_from_path(bs4)
        io.start(
            'Adding bootstrap 3 theme {} and bootstrap 4 theme {} to bootstrap themes'.format(
                highlight(bs3_name),
                highlight(bs4_name)))
    else:
        io.start(
            'Adding bootstrap 3 theme {} to bootstrap themes'.format(
                highlight(bs3_name)))
    if not args.from_path:
        paths = [_get_path_from_quick_folders(theme) for theme in paths]
    files = _prepare_files_for_upload(paths, names, valid_types)
    post_files(files, api_)


@command
def add_logo(args):
    """
    add_logo uploads a logo to add to the left top of the menu
    :param args: commandline arguments containing path to logo
    :return: None
    """
    api_ = api.logo()
    valid_types = {'image/jpeg', 'image/png', 'image/gif'}
    logo = [args.logo]
    if not args.from_path:
        io.start('Adding logo from path {}'.format(highlight(args.logo)))
        logo = [_get_path_from_quick_folders(args.logo)]
    else:
        io.start('Adding logo {}'.format(highlight(args.logo)))
    files = _prepare_files_for_upload(logo, ['logo'], valid_types)
    post_files(files, api_)


def _prepare_files_for_upload(paths, names, valid_content_types):
    """
    _prepare_files_for_upload takes the paths to the files to upload, the names of them and a list of valid content
    types to translate to content types and generates a dictionary which can be uploaded in a post request
    :param paths: a list of paths to the files to upload
    :param names: the names of files to upload
    :param valid_content_types: set of the possible valid content types
    :return: a dictionary with as key the name of the file and as value a tuple with: filename, file to upload, and
    content type

    :exception McmdError when the file on the given path does not exist and when the content type of the file is
    invalid.
    """
    files = {}
    for name, path in zip(names, paths):
        file_name = get_file_name_from_path(path)
        content_type = mimetypes.guess_type(path)[0]
        if not os_path.exists(path):
            raise McmdError(
                'File [{}] does not exist on path [{}]'.format(file_name, path.strip(file_name)))
        elif content_type in valid_content_types:
            try:
                files[name] = (file_name, open(path, 'rb'), content_type)
            except FileNotFoundError:
                raise McmdError(
                    'File [{}] does not exist on path [{}]'.format(file_name, path.strip(file_name)))
        else:
            raise McmdError(
                'File [{}] does not have valid content type [{}], '
                'content type should be in {}'.format(file_name,
                                                      content_type,
                                                      valid_content_types))
    return files


def _get_path_from_quick_folders(file_name):
    file_name = os_path.splitext(file_name)[0]
    file_map = scan_folders_for_files(context().get_resource_folders())
    path = select_path(file_map, file_name)
    return str(path)


def _validate_args(args):
    """To make the bootstrap themes as backwards compatible as possible make both bootstrap3 and 4 named, but only
    bootstrap3 required, in future 4 will be required and 3 will be removed eventually."""
    if args.type == 'theme' and not args.bootstrap3:
        p_add_theme.error("the following argument is required: bootstrap3")
