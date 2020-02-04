import collections
import json
import textwrap
from argparse import RawDescriptionHelpFormatter
from typing import Optional, List
from urllib.parse import urljoin

from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.core.compatibility import version
from mcmd.core.errors import McmdError
from mcmd.io import io, ask
from mcmd.io.io import highlight
from mcmd.molgenis import api
from mcmd.molgenis.client import post, get, put

Membership = collections.namedtuple('Membership', ['id', 'role_name', 'role_label', 'group_name'])


# =========
# Arguments
# =========

@arguments('make')
def add_arguments(subparsers):
    p_make = subparsers.add_parser('make',
                                   help='make a user member of a role',
                                   formatter_class=RawDescriptionHelpFormatter,
                                   description=textwrap.dedent(
                                       """
                                       Make a user member of a (group-) role. 
                                       
                                       Note: since MOLGENIS 8.3 group and role names are case sensitive and need
                                       to be typed exactly as-is. (Before 8.3 all role names will be upper cased 
                                       automatically).
                                       
                                       Example usage:
                                         mcmd make john Biobanks_MANAGER
                                         mcmd make jane GCC_EDITOR                                        
                                       """
                                   ))
    p_make.set_defaults(func=make,
                        write_to_history=True)
    p_make.add_argument('user',
                        type=str,
                        help='the user to make a member')
    p_make.add_argument('role',
                        type=str,
                        help='the role to make the user a member of')


# =======
# Methods
# =======

@command
def make(args):
    role_name = _to_role_name(args.role)
    group_name = _find_group(role_name)
    membership = _get_user_group_membership(args.user, group_name)
    if membership:
        if membership.role_name == role_name:
            io.info('User {} is already {} of group {}'.format(highlight(args.user),
                                                               highlight(membership.role_label),
                                                               highlight(group_name)))
        else:
            update = ask.confirm(
                'User {} is {} of group {}. Do you want to update his/her role to {}?'.format(args.user,
                                                                                              membership.role_label,
                                                                                              group_name,
                                                                                              role_name))
            if update:
                _update_membership(args.user, group_name, role_name)
    else:
        _add_membership(args.user, group_name, role_name)


def _add_membership(user: str, group_name: str, role: str):
    io.start('Making user {} a member of role {}'.format(highlight(user), highlight(role)))
    url = api.member(group_name)
    post(url, data={'username': user, 'roleName': role})


def _update_membership(user: str, group_name: str, role: str):
    io.start('Making user {} a member of role {}'.format(highlight(user), highlight(role)))
    url = urljoin(api.member(group_name), user)
    put(url, data=json.dumps({'roleName': role}))


def _find_group(role_name: str) -> str:
    io.debug('Fetching groups')
    response = get(api.rest2('sys_sec_Role'),
                   params={
                       'attrs': 'group(name)',
                       'q': 'name=={}'.format(role_name)
                   })

    if len(response.json()['items']) == 0:
        raise McmdError('Role {} not found'.format(role_name))

    role = response.json()['items'][0]

    if 'group' not in role:
        raise McmdError('Role {} is not a group role'.format(role_name))

    return role['group']['name']


def _get_user_group_membership(user: str, group_name: str) -> Optional[Membership]:
    io.debug('Checking if user is already member of this group')

    for membership in _get_memberships_for_user(user):
        if membership.group_name == group_name:
            return membership

    return None


def _get_memberships_for_user(user_name: str) -> List[Membership]:
    users = get(api.rest2('sys_sec_User'),
                params={
                    'attrs': 'id',
                    'q': 'username=={}'.format(user_name)
                }).json()['items']
    if len(users) == 0:
        raise McmdError('Unknown user {}'.format(user_name))

    user_id = users[0]['id']

    memberships = get(api.rest2('sys_sec_RoleMembership'),
                      params={
                          'attrs': 'id,user(username),role(name,label,group(name))',
                          'q': 'user=={}'.format(user_id)
                      }).json()['items']

    return [
        Membership(id=m['id'],
                   role_name=m['role']['name'],
                   role_label=m['role']['label'],
                   group_name=m['role']['group']['name'])
        for m in memberships
    ]


@version('7.0.0')
def _to_role_name(role_input: str):
    """Before 8.3.0 all role names are upper case."""
    return role_input.upper()


@version('8.3.0')
def _to_role_name(role_input: str):
    """Since 8.3.0 role names are case sensitive."""
    return role_input
