from mdev import io
from mdev.client.molgenis_client import login, post
from mdev.config.config import get_config
from mdev.io import highlight

config = get_config()


def add_user(args):
    io.start('Adding user %s' % highlight(args.username))
    login(args)
    post(config.get('api', 'rest1') + 'sys_sec_User',
         {'username': args.username,
          'password_': args.username,
          'Email': args.username + "@molgenis.org",
          'active': True})


def add_group(args):
    io.start('Adding group %s' % highlight(args.name))
    login(args)
    post(config.get('api', 'group'), {'name': args.name, 'label': args.name})
