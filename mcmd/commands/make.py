"""
Makes a user a member of a role.

Differentiates between 'normal' roles and 'group' roles:
- Normal roles are roles that do not belong to a group. A user can be a member of more than one of these roles.
- Group roles are roles that belong to a group. A user can be a member of just one of a group's roles.

This command won't do anything if a user is already member of the specified role. In the case a user is already member
of another role within the same group, this command will ask for confirmation before updating it.
"""

import json
import textwrap
from argparse import RawDescriptionHelpFormatter
from typing import Optional, List
from urllib.parse import urljoin

from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.core.errors import McmdError
from mcmd.io import io, ask
from mcmd.io.io import highlight
from mcmd.molgenis import api
from mcmd.molgenis.client import post, get, put
from mcmd.molgenis.principals import to_role_name
from mcmd.molgenis.rest_api_v2_mapper import map_to_role, map_to_user, map_to_role_membership
from mcmd.molgenis.system import User, Group, Role, RoleMembership
from mcmd.utils.time import timestamp


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
    role_name = to_role_name(args.role)
    role = _get_role(role_name)
    user = _get_user(args.user)
    if role.group:
        _make_member_of_group_role(user, role)
    else:
        _make_member_of_role(role, user)


def _make_member_of_group_role(user: User, role: Role):
    group = role.group
    membership = _get_group_membership(user, group)
    if membership:
        if membership.role.name == role.name:
            io.info('User {} is already {} of group {}'.format(highlight(user.username),
                                                               highlight(role.label),
                                                               highlight(group.name)))
        else:
            update = ask.confirm(
                'User {} is {} of group {}. Do you want to update his/her role to {}?'.format(user.username,
                                                                                              membership.role.label,
                                                                                              group.name,
                                                                                              role.label))
            if update:
                _update_group_role_membership(user, group, role)
    else:
        _add_group_role_membership(user, group, role)


def _make_member_of_role(role, user):
    if _is_member(user, role):
        io.info('User {} is already a member of role {}'.format(highlight(user.username), highlight(role.name)))
    else:
        _add_role_membership(user, role)


def _add_group_role_membership(user: User, group: Group, role: Role):
    io.start('Making user {} a member of role {}'.format(highlight(user.username), highlight(role.name)))
    url = api.member(group.name)
    post(url, data={'username': user.username, 'roleName': role.name})


def _update_group_role_membership(user: User, group: Group, role: Role):
    io.start('Making user {} a member of role {}'.format(highlight(user.username), highlight(role.name)))
    url = urljoin(api.member(group.name), user.username)
    put(url, data=json.dumps({'roleName': role.name}))


def _add_role_membership(user: User, role: Role):
    """
    Adds a membership manually because the identities API can't add memberships to non-group roles.
    """
    io.start('Making user {} a member of role {}'.format(highlight(user.username), highlight(role.name)))
    membership = {'user': user.id,
                  'role': role.id,
                  'from': timestamp()}
    data = {'entities': [membership]}
    post(api.rest2('sys_sec_RoleMembership'), data=data)


def _get_group_membership(user: User, group: Group) -> Optional[RoleMembership]:
    group_roles = _get_group_roles(group)
    group_role_ids = [role.id for role in group_roles]

    memberships = get(api.rest2('sys_sec_RoleMembership'),
                      params={
                          'attrs': 'id,user(id,username),role(id,name,label,group(id,name))',
                          'q': 'user=={};role=in=({});(to=='',to=ge={})'.format(user.id, ','.join(group_role_ids),
                                                                                timestamp())
                      }).json()['items']

    if len(memberships) == 0:
        return None
    else:
        return map_to_role_membership(memberships[0])


def _get_group_roles(group: Group) -> List[Role]:
    roles = get(api.rest2('sys_sec_Role'),
                params={
                    'attrs': 'id,name,label,group(id,name)',
                    'q': 'group=={}'.format(group.id)
                }).json()['items']

    if len(roles) == 0:
        raise McmdError('No roles found for group {}'.format(group.name))

    return [map_to_role(role) for role in roles]


def _is_member(user: User, role: Role) -> bool:
    memberships = get(api.rest2('sys_sec_RoleMembership'),
                      params={
                          'attrs': 'id',
                          'q': "user=={};role=={};(to=='',to=ge={})".format(user.id, role.id, timestamp())
                      }).json()['items']

    return len(memberships) > 0


def _get_user(user_name: str) -> User:
    users = get(api.rest2('sys_sec_User'),
                params={
                    'attrs': 'id,username',
                    'q': 'username=={}'.format(user_name)
                }).json()['items']

    if len(users) == 0:
        raise McmdError('Unknown user {}'.format(user_name))
    else:
        return map_to_user(users[0])


def _get_role(role_name: str) -> Role:
    roles = get(api.rest2('sys_sec_Role'),
                params={
                    'attrs': 'id,name,label,group(id,name)',
                    'q': 'name=={}'.format(role_name)
                }).json()['items']

    if len(roles) == 0:
        raise McmdError('No role found with name {}'.format(role_name))
    else:
        return map_to_role(roles[0])
