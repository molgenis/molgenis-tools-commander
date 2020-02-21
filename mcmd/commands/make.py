"""
Makes a user a member of a role or includes a group role in another role.

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
from mcmd.core.compatibility import version
from mcmd.core.errors import McmdError
from mcmd.io import io, ask
from mcmd.io.io import highlight
from mcmd.molgenis import api
from mcmd.molgenis.client import post, get, put
from mcmd.molgenis.principals import to_role_name, get_principal_type_from_args, PrincipalType
from mcmd.molgenis.rest_api_v2_mapper import map_to_role, map_to_user, map_to_role_membership
from mcmd.molgenis.system import User, Group, Role, RoleMembership
from mcmd.molgenis.version import get_version
from mcmd.utils.time import timestamp


# =========
# Arguments
# =========

@arguments('make')
def add_arguments(subparsers):
    p_make = subparsers.add_parser('make',
                                   help='make a user or role member of a role',
                                   formatter_class=RawDescriptionHelpFormatter,
                                   description=textwrap.dedent(
                                       """
                                       Make a user or role member of a (group) role.  
                                       
                                       When no subject type is specified (with --user or --role), the Commander will 
                                       try to detect it. 
                                       
                                       Version notes: 
                                       - since MOLGENIS 8.1 it is possible to let roles include group roles (can be
                                         used to make role ANONYMOUS or USER member of a group).
                                       - since MOLGENIS 8.3 group and role names are case sensitive and need
                                         to be typed exactly as-is. (Before 8.3 all role names will be upper cased 
                                         automatically).
                                       
                                       example usage:
                                         mcmd make john Biobanks_MANAGER
                                         mcmd make jane GCC_EDITOR                                        
                                         mcmd make --user jane GCC_EDITOR
                                         mcmd make --role ANONYMOUS GCC_VIEWER
                                       """
                                   ))
    p_make.set_defaults(func=make,
                        write_to_history=True)
    p_make.add_argument('subject',
                        type=str,
                        help='the user or role')
    p_make.add_argument('target_role',
                        metavar='role',
                        type=str,
                        help='the role to make the subject a member of')
    p_make_subject = p_make.add_mutually_exclusive_group()
    p_make_subject.add_argument('--user', '-u',
                                action='store_true',
                                help='flag to specify that the subject is a user')
    p_make_subject.add_argument('--role', '-r',
                                action='store_true',
                                help='flag to specify that the subject is a role')


# =======
# Methods
# =======

@command
def make(args):
    role_name = to_role_name(args.target_role)
    role = _get_role(role_name)
    subject_type = _get_subject_type(args)
    if subject_type == PrincipalType.USER:
        user = _get_user(args.subject)
        if role.group:
            _make_member_of_group_role(user, role)
        else:
            _make_member_of_role(role, user)
    elif subject_type == PrincipalType.ROLE:
        subject = _get_role(args.subject)
        _include_group_role(subject, role)
    else:
        raise ValueError("Unknown principal type")


# noinspection PyUnusedLocal
@version('7.0.0')
def _get_subject_type(args) -> PrincipalType:
    """
    Prior to 8.1 roles can't be included with the identities API so the subject is always a user.
    """
    if args.role:
        raise McmdError(
            "Including group roles is only possible in MOLGENIS 8.3 and up (you are using {})".format(get_version()))
    else:
        return PrincipalType.USER


@version('8.1.0')
def _get_subject_type(args) -> PrincipalType:
    """
    From 8.3 and up, group roles can be included with the identities API so the subject can be a user or a role.
    """
    return get_principal_type_from_args(args, principal_name=args.subject)


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


@version('8.1.0')
def _include_group_role(subject: Role, target_role: Role):
    if not target_role.group:
        raise McmdError('Role {} is not a group role'.format(target_role.name))
    if subject.name == target_role.name:
        raise McmdError("A role can't include itself")

    io.start('Including role {} in role {}'.format(highlight(target_role.name), highlight(subject.name)))
    include = {'role': target_role.name}
    put(api.role(target_role.group.name, subject.name), data=json.dumps(include))


def _get_group_membership(user: User, group: Group) -> Optional[RoleMembership]:
    group_roles = _get_group_roles(group)
    group_role_ids = [role.id for role in group_roles]

    memberships = get(api.rest2('sys_sec_RoleMembership'),
                      params={
                          'attrs': 'id,user(id,username),role(id,name,label,group(id,name))',
                          'q': "user=={};role=in=({});(to=='',to=ge={})".format(user.id, ','.join(group_role_ids),
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
