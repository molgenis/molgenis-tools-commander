from mdev import io
from mdev.client.molgenis_client import login, post, get
from mdev.config.config import config
from mdev.io import highlight
from mdev.utils import MdevError, is_true_or_false


# =========
# Arguments
# =========

def arguments(subparsers):
    p_add = subparsers.add_parser('add',
                                  help='Add users and groups',
                                  description="Run 'mdev add group -h' or 'mdev add user -h' to view the help for those"
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
                            nargs=1,
                            help="The user's password")
    p_add_user.add_argument('--with-email', '-e',
                            metavar='EMAIL',
                            type=str,
                            nargs=1,
                            help="The user's e-mail address")
    p_add_user.add_argument('--is-active', '-a',
                            metavar='TRUE/FALSE',
                            # with bool the default option is not working
                            type=str,
                            nargs=1,
                            default="true",
                            help="Is the user active? (default: true)")
    p_add_user.add_argument('--is-superuser', '-s',
                            metavar='TRUE/FALSE',
                            # with bool the default option is not working
                            type=str,
                            nargs=1,
                            default="false",
                            help="Is the user superuser? (default: false)")

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


# =======
# Methods
# =======

def add_user(args):
    io.start('Adding user %s' % highlight(args.username))
    login(args)

    password = args.set_password[0] if args.set_password else args.username
    email = args.with_email[0] if args.with_email else args.username + '@molgenis.org'

    active = str(is_true_or_false(args.is_active[0]))
    error_message = '{} should be a boolean, cannot transform [{}] to boolean'
    if active == 'None':
        raise MdevError(error_message.format('--is-active', args.is_active[0]))

    superuser = str(is_true_or_false(args.is_superuser[0]))
    if superuser == 'None':
        raise MdevError(error_message.format('--is-superuser', args.is_superuser[0]))

    post(config().get('api', 'rest1') + 'sys_sec_User',
         {'username': args.username,
          'password_': password,
          'Email': email,
          'active': active,
          'superuser': superuser
          })


def add_group(args):
    io.start('Adding group %s' % highlight(args.name))
    login(args)
    post(config().get('api', 'group'), {'name': args.name, 'label': args.name})


def add_package(args):
    io.start('Adding package %s' % highlight(args.id))
    login(args)

    data = {'id': args.id,
            'label': args.id}

    if args.parent:
        data['parent'] = args.parent

    post(config().get('api', 'rest1') + 'sys_md_Package', data)


def add_token(args):
    io.start('Adding token %s for user %s' % (highlight(args.token), highlight(args.user)))
    login(args)

    user = get(config().get('api', 'rest2') + 'sys_sec_User?attrs=id&q=username==%s' % args.user)
    if user.json()['total'] == 0:
        raise MdevError('Unknown user %s' % args.user)

    user_id = user.json()['items'][0]['id']

    data = {'User': user_id,
            'token': args.token}

    post(config().get('api', 'rest1') + 'sys_sec_Token', data)