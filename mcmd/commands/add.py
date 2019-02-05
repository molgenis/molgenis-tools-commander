import mcmd.config.config as config
from mcmd import io
from mcmd.client.molgenis_client import login, post, get, import_files
from mcmd.io import highlight
from mcmd.utils import McmdError, get_file_name_from_path


# =========
# Arguments
# =========

def arguments(subparsers):
    p_add = subparsers.add_parser('add',
                                  help='Add users and groups',
                                  description="Run 'mcmd add group -h' or 'mcmd add user -h' to view the help for those"
                                              " sub-commands")
    p_add_subparsers = p_add.add_subparsers(dest="type")

    p_add_group = p_add_subparsers.add_parser('group',
                                              help='Add a group')
    p_add_group.set_defaults(func=add_group,
                             write_to_history=True)
    p_add_group.add_argument('name',
                             type=str,
                             help="The group's name")

    p_add_user = p_add_subparsers.add_parser('user',
                                             help='Add a user')
    p_add_user.set_defaults(func=add_user,
                            write_to_history=True)
    p_add_user.add_argument('username',
                            type=str,
                            help="The user's name")
    p_add_user.add_argument('--set-password', '-p',
                            metavar='PASSWORD',
                            type=str,
                            help="The user's password")
    p_add_user.add_argument('--with-email', '-e',
                            metavar='EMAIL',
                            type=str,
                            help="The user's e-mail address")
    p_add_user.add_argument('--is-inactive', '-a',
                            action='store_true',
                            help="Make user inactive")
    p_add_user.add_argument('--is-superuser', '-s',
                            action='store_true',
                            help="Make user superuser")
    p_add_user.add_argument('--change-password', '-c',
                            action='store_true',
                            help="Set change password to true for user")

    p_add_package = p_add_subparsers.add_parser('package',
                                                help='Add a package')
    p_add_package.set_defaults(func=add_package,
                               write_to_history=True)
    p_add_package.add_argument('id',
                               type=str,
                               help="The id of the Package")
    p_add_package.add_argument('--in',
                               type=str,
                               dest='parent',
                               help="The id of the parent")

    p_add_token = p_add_subparsers.add_parser('token',
                                              help='Add a token')
    p_add_token.set_defaults(func=add_token,
                             write_to_history=True)
    p_add_token.add_argument('user',
                             type=str,
                             help="The user to give the token to")
    p_add_token.add_argument('token',
                             type=str,
                             help="The token")

    p_add_theme = p_add_subparsers.add_parser('theme',
                                              help='Upload a bootstrap theme')
    p_add_theme.set_defaults(func=add_theme,
                             write_to_history=True)
    p_add_theme.add_argument('bs3',
                             type=str,
                             metavar='Bootstrap 3 theme',
                             help="The bootstrap 3 css theme file")
    p_add_theme.add_argument('--bs4',
                             type=str,
                             metavar='Bootstrap 4 theme',
                             help="The bootstrap4 css theme file (when not specified, the default molgenis theme will "
                                  "be applied on bootstrap4 pages")


# =======
# Methods
# =======

@login
def add_user(args):
    io.start('Adding user %s' % highlight(args.username))

    password = args.set_password if args.set_password else args.username
    email = args.with_email if args.with_email else args.username + '@molgenis.org'
    active = not args.is_inactive
    superuser = args.is_superuser
    ch_pwd = args.change_password

    post(config.api('rest1') + 'sys_sec_User',
         {'username': args.username,
          'password_': password,
          'changePassword': ch_pwd,
          'Email': email,
          'active': active,
          'superuser': superuser
          })


@login
def add_group(args):
    io.start('Adding group %s' % highlight(args.name))
    post(config.api('group'), {'name': args.name.lower(), 'label': args.name})


@login
def add_package(args):
    io.start('Adding package %s' % highlight(args.id))

    data = {'id': args.id,
            'label': args.id}

    if args.parent:
        data['parent'] = args.parent

    post(config.api('rest1') + 'sys_md_Package', data)


@login
def add_token(args):
    io.start('Adding token %s for user %s' % (highlight(args.token), highlight(args.user)))

    user = get(config.api('rest2') + 'sys_sec_User?attrs=id&q=username==%s' % args.user)
    if user.json()['total'] == 0:
        raise McmdError('Unknown user %s' % args.user)

    user_id = user.json()['items'][0]['id']

    data = {'User': user_id,
            'token': args.token}

    post(config.api('rest1') + 'sys_sec_Token', data)


@login
def add_theme(args):
    """
    add_theme adds a theme to the stylesheet table
    :param args: commandline arguments containing bootstrap3_theme and optionally bootstrap4_theme
    :return: None
    :exception MdevError: when provided path to one of the files is not a file
    """
    bs3 = args.bs3
    bs3_name = get_file_name_from_path(bs3)
    bs4 = args.bs4
    extension = 'css'
    content_type = 'text/css'
    api = config.api('add_theme')

    if not bs3_name.endswith(extension):
        raise McmdError('Bootstrap 3 file: [{}] is not a valid css file.'.format(bs3_name))
    try:
        files = {'bootstrap3-style': (bs3_name, open(bs3, 'rb'), content_type)}
    except FileNotFoundError:
        raise McmdError('Bootstrap 3 file: [{}] does not exist on path: [{}]'.format(bs3_name, bs3.strip(bs3_name)))

    if bs4:
        bs4_name = get_file_name_from_path(bs4)
        if not bs4_name.endswith(extension):
            raise McmdError('Bootstrap 4 file: [{}] is not a valid css file.'.format(bs4_name))
        else:
            io.start(
                'Adding bootstrap 3 theme: {} and bootstrap 4 theme: {} to bootstrap themes'.format(
                    highlight(bs3_name),
                    highlight(bs4_name)))
            try:
                files['bootstrap4-style'] = (bs4_name, open(bs4, 'rb'), content_type)
            except FileNotFoundError:
                raise McmdError(
                    'Bootstrap 4 file: [{}] does not exist on path: [{}]'.format(bs4_name, bs4.strip(bs4_name)))
    else:
        io.start(
            'Adding bootstrap 3 theme: {} to bootstrap themes (default molgenis style will be applied on pages using bootstrap 4)'.format(
                highlight(bs3_name)))
    import_files(files, api)
