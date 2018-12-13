from mcmd import io
from mcmd.client.molgenis_client import login, post, get
from mcmd.config.config import config
from mcmd.io import highlight
from mcmd.utils import lower_kebab, McmdError, upper_snake


# =========
# Arguments
# =========

def arguments(subparsers):
    p_make = subparsers.add_parser('make',
                                   help='Make a user member of a role')
    p_make.set_defaults(func=make,
                        write_to_history=True)
    p_make.add_argument('user',
                        type=str,
                        help='The user to make a member')
    p_make.add_argument('role',
                        type=str,
                        help='The role to make the user a member of')


# =======
# Methods
# =======

@login
def make(args):
    io.start('Making user %s a member of role %s' % (highlight(args.user), highlight(args.role.upper())))

    group_name = _find_group(args.role)

    url = config().get('api', 'member') % group_name
    post(url, {'username': args.user, 'roleName': args.role.upper()})


def _find_group(role):
    io.debug('Fetching groups')
    groups = get(config().get('api', 'rest2') + 'sys_sec_Group?attrs=name')
    role = lower_kebab(role)

    matches = {len(group['name']): group['name'] for group in groups.json()['items'] if role.startswith(group['name'])}

    if not matches:
        raise McmdError('No group found for role %s' % upper_snake(role))

    return matches[max(matches, key=int)]
