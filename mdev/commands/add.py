from mdev import io
from mdev.client.molgenis_client import login, post, get, resource_exists, ResourceType, import_logo
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import MdevError, file_to_string, string_to_json
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
    :exception: MdevError: when path in argument is not a file
    """
    io.start('Adding logo from path: {}'.format(args.logo))
    login(args)
    filePath = Path(args.logo)
    # Check if commandline argument is a file
    if filePath.is_file():
        # TODO: Work with the quick paths
        import_logo(args.logo)
    else:
        raise MdevError("Provided path: {} is not a file".format(args.logo))
