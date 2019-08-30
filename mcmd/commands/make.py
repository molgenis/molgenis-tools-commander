from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.io import io, ask
from mcmd.io.io import highlight
from mcmd.molgenis import api
from mcmd.molgenis.client import post, get, put
from mcmd.utils.utils import lower_kebab, upper_snake

Membership = collections.namedtuple('Membership', ['id', 'role_name', 'role_label', 'group_name'])


# =========
# Arguments
# =========

@arguments('make')
def add_arguments(subparsers):
    p_make = subparsers.add_parser('make',
                                   help='make a user member of a role')
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

@command
def make(args):
    group_name = _find_group(args.role)
    membership = _get_user_group_membership(args.user, group_name)
    if membership:
        if membership.role_name == args.role.upper():
            io.info('User {} is already {} of group {}'.format(highlight(args.user),
                                                               highlight(membership.role_label),
                                                               highlight(group_name)))
        else:
            update = ask.confirm(
                'User {} is {} of group {}. Do you want to update his/her role to {}?'.format(args.user,
                                                                                              membership.role_label,
                                                                                              group_name,
                                                                                              args.role.upper()))
            if update:
                _update_membership(args.user, group_name, args.role)
    else:
        _add_membership(args.user, group_name, args.role)


def _add_membership(user: str, group_name: str, role: str):
    io.start('Making user {} a member of role {}'.format(highlight(user), highlight(role.upper())))
    url = api.member(group_name)
    post(url, data={'username': user, 'roleName': role.upper()})


def _update_membership(user: str, group_name: str, role: str):
    io.start('Making user {} a member of role {}'.format(highlight(user), highlight(role.upper())))
    url = urljoin(api.member(group_name), user)
    put(url, data=json.dumps({'roleName': role.upper()}))


def _find_group(role: str):
    io.debug('Fetching groups')
    groups = get(api.rest2('sys_sec_Group'),
                 params={
                     'attrs': 'id,name'
                 })
    role = lower_kebab(role)

    matches = {len(group['name']): group['name'] for group in groups.json()['items'] if role.startswith(group['name'])}

    if not matches:
        raise McmdError('No group found for role %s' % upper_snake(role))

    return matches[max(matches, key=int)]


def _get_user_group_membership(user: str, group_name: str) -> Optional[Membership]:
    io.debug('Checking if user is already member of this group')

    for membership in _get_memberships_for_user(user):
        if membership.group_name == group_name:
            return membership

    return None


def _get_memberships_for_user(user_name: str) -> List[Membership]:
    # Don't use a query here because the indexer might not've finished yet
    memberships = get(api.rest2('sys_sec_RoleMembership'),
                      params={
                          'attrs': 'id,user(username),role(name,label,group(name))'
                      }).json()['items']
    return [
        Membership(id=m['id'],
                   role_name=m['role']['name'],
                   role_label=m['role']['label'],
                   group_name=m['role']['group']['name'])
        for m in memberships if m['user']['username'] == user_name
    ]
