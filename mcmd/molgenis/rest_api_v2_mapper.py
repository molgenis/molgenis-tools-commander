"""
Maps json items from the REST API v2 to value objects from the 'system' module.
"""

from mcmd.molgenis.system import Role, Group, User, RoleMembership


def map_to_role(role: dict) -> Role:
    group = None
    if 'group' in role:
        group = map_to_group(role['group'])

    return Role(id=role['id'],
                name=role['name'],
                label=role['label'],
                group=group)


def map_to_user(user: dict) -> User:
    return User(id=user['id'],
                username=user['username'])


def map_to_group(group: dict) -> Group:
    return Group(id=group['id'],
                 name=group['name'])


def map_to_role_membership(membership: dict) -> RoleMembership:
    role = membership['role']
    user = membership['user']
    return RoleMembership(id=membership['id'],
                          user=map_to_user(user),
                          role=map_to_role(role))
