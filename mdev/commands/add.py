from mdev import io
from mdev.client.molgenis_client import login, post, get, resource_exists, ResourceType, import_logo, \
    import_bootstrap_theme
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import MdevError, file_to_string, string_to_json, get_file_name_from_path
from pathlib import Path

config = get_config()


def add_user(args):
    io.start('Adding user %s' % highlight(args.username))
    login(args)

    password = args.with_password if args.with_password else args.username
    email = args.with_email if args.with_email else args.username + '@molgenis.org'

    post(config.get('api', 'rest1') + 'sys_sec_User',
         {'username': args.username,
          'password_': password,
          'Email': email,
          'active': args.is_active})


def add_group(args):
    io.start('Adding group %s' % highlight(args.name))
    login(args)
    post(config.get('api', 'group'), {'name': args.name, 'label': args.name})


def add_package(args):
    io.start('Adding package %s' % highlight(args.id))
    login(args)

    data = {'id': args.id,
            'label': args.id}

    if args.parent:
        data['parent'] = args.parent

    post(config.get('api', 'rest1') + 'sys_md_Package', data)


def add_token(args):
    io.start('Adding token %s for user %s' % (highlight(args.token), highlight(args.user)))
    login(args)

    user = get(config.get('api', 'rest2') + 'sys_sec_User?attrs=id&q=username==%s' % args.user)
    if user.json()['total'] == 0:
        raise MdevError('Unknown user %s' % args.user)

    user_id = user.json()['items'][0]['id']

    data = {'User': user_id,
            'token': args.token}

    post(config.get('api', 'rest1') + 'sys_sec_Token', data)


def add_rows(args):
    """
    add_rows calls a post request to add rows to the specified table
    :param args: commandline arguments containing entityType and rows
    :return: None
    """
    io.start('Adding rows to entity type {}'.format(args.entityType))
    login(args)
    if not resource_exists(args.entityType, ResourceType.ENTITY_TYPE):
        raise MdevError("Entity type {} doesn't exist".format(args.entityType))

    content = args.rows
    file = Path(args.rows)
    # Check if commandline argument is a file
    if file.is_file():
        content = file_to_string(args.rows)

    # TODO: Work with the quick paths
    json_structure = string_to_json(content)
    data = {'entities': json_structure}
    url = '{}{}'.format(config.get('api', 'rest2'), args.entityType)
    post(url, data)


def add_logo(args):
    """
    add_logo uploads a logo to add to the left top of the menu
    :param args:
    :return: None
    :exception MdevError: when path in argument is not a file
    """
    io.start('Adding logo from path: {}'.format(args.logo))
    login(args)

    if _is_file(args.logo):
        # TODO: Work with the quick paths
        import_logo(args.logo)
    else:
        _not_a_file_error(args.logo)


def add_theme(args):
    """
    add_theme adds a theme to the stylesheet table
    :param args: commandline arguments containing bootstrap3_theme and optionally bootstrap4_theme
    :return: None
    :exception MdevError: when provided path to one of the files is not a file
    """
    bs3 = args.bootstrap3_theme
    bs3_name = get_file_name_from_path(bs3)
    login(args)
    bs4 = args.bootstrap4_theme

    if _is_file(bs3):
        # TODO: Work with the quick paths
        if bs4:
            if _is_file(bs4):
                bs4_name = get_file_name_from_path(bs4)
                io.start(
                    'Adding bootstrap3 theme: {} and bootstrap4 theme: {} to bootstrap themes'.format(
                        highlight(bs3_name),
                        highlight(bs4_name)))
                import_bootstrap_theme(bs3, bs4)
            else:
                _not_a_file_error(bs4)
        else:
            io.start(
                'Adding bootstrap3 theme: {} to bootstrap themes (default molgenis style will be applied on pages using bootstrap4)'.format(
                    highlight(bs3_name)))
            import_bootstrap_theme(bs3)
    else:
        _not_a_file_error(bs3)


def _not_a_file_error(path):
    """
    _not_a_file_error raises exception telling the user that the provided path is not a file
    :param path: the invalid path
    :exception MdevError: when called
    """
    raise MdevError("Provided path: {} is not a file".format(path))


def _is_file(potential_file):
    """
    _is_file checks if provided potential file is a file
    :param potential_file: path to potential file
    :return: True when path is a file, else False
    """
    test_file = Path(potential_file)
    return test_file.is_file()
