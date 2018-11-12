from mdev import io
from mdev.client.molgenis_client import login, post, get
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import MdevError

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

def add_row(args):
    io.start
