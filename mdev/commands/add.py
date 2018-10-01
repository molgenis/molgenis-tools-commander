from mdev import io
from mdev.client.molgenis_client import login, post
from mdev.config.config import get_config
from mdev.io import highlight

config = get_config()


def add(args):
    if args.type == 'user':
        io.start('Adding user %s' % highlight(args.value))
        login(args)
        _add_user(args.value)
    elif args.type == 'group':
        io.start('Adding group %s' % highlight(args.value))
        login(args)
        _add_group(args.value)


def _add_user(username):
    post(config.get('api', 'rest1') + 'sys_sec_User',
         {'username': username,
          'password_': username,
          'Email': username + "@molgenis.org",
          'active': True})


def _add_group(name):
    post(config.get('api', 'group'), {'name': name, 'label': name})
