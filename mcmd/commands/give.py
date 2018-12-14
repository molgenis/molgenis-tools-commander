"""
Give a principal (a user or a group) some permission on a resource (a package, entity type or plugin). Unless specified
by the user, the give command will try to figure out the principal- and resource types itself. If a resource or
principal doesn't exist, the program will terminate.
"""

from mcmd import io
from mcmd.client.molgenis_client import login, grant, PrincipalType, principal_exists, \
    resource_exists, ResourceType, ensure_resource_exists, ensure_principal_exists
from mcmd.io import multi_choice, highlight
from mcmd.utils import McmdError


# =========
# Arguments
# =========

def arguments(subparsers):
    p_give = subparsers.add_parser('give',
                                   help='Give permissions on resources to roles or users.')
    p_give.set_defaults(func=give,
                        write_to_history=True)
    p_give_resource = p_give.add_mutually_exclusive_group()
    p_give_resource.add_argument('--entity-type', '-e',
                                 action='store_true',
                                 help='Flag to specify that the resource is an entity type')
    p_give_resource.add_argument('--package', '-p',
                                 action='store_true',
                                 help='Flag to specify that the resource is a package')
    p_give_resource.add_argument('--plugin', '-pl',
                                 action='store_true',
                                 help='Flag to specify that the resource is a plugin')
    p_give_receiver = p_give.add_mutually_exclusive_group()
    p_give_receiver.add_argument('--user', '-u',
                                 action='store_true',
                                 help='Flag to specify that the receiver is a user')
    p_give_receiver.add_argument('--role', '-r',
                                 action='store_true',
                                 help='Flag to specify that the receiver is a role')
    p_give.add_argument('receiver',
                        type=str,
                        help='The role (or user) to give the permission to')
    p_give.add_argument('permission',
                        choices=['none', 'writemeta', 'readmeta', 'write', 'edit', 'read', 'view', 'count'],
                        help='The permission type to give. Synonyms are allowed (e.g. write/edit).')
    p_give.add_argument('resource',
                        type=str,
                        help='The resource to which permission is given')


# =======
# Globals
# =======


_PERMISSION_SYNONYMS = {'view': 'read',
                        'edit': 'write'}


# =======
# Methods
# =======

@login
def give(args):
    # Convert synonyms to correct permission type
    if args.permission in _PERMISSION_SYNONYMS:
        args.permission = _PERMISSION_SYNONYMS[args.permission]

    # The PermissionManagerController always gives 200 OK so we need to validate everything ourselves
    resource_type = _get_resource_type(args)
    principal_type = _get_principal_type(args)
    io.start('Giving %s %s permission to %s on %s %s' % (principal_type.value,
                                                         highlight(args.receiver),
                                                         highlight(args.permission),
                                                         resource_type.get_label().lower(),
                                                         highlight(args.resource)))

    grant(principal_type, args.receiver, resource_type, args.resource, args.permission)


def _get_principal_type(args):
    principal_name = args.receiver
    if args.user:
        ensure_principal_exists(args.user, principal_name)
        return PrincipalType.USER
    elif args.role:
        ensure_principal_exists(args.role, principal_name)
        return PrincipalType.ROLE
    else:
        return _guess_principal_type(principal_name)


def _guess_principal_type(principal_name):
    results = dict()
    for principal_type in PrincipalType:
        if principal_exists(principal_name, principal_type):
            results[principal_type.value] = principal_name

    if len(results) == 0:
        raise McmdError('No principals found with name %s' % principal_name)
    elif len(results) > 1:
        choices = results.keys()
        answer = multi_choice('Multiple principals found with name %s. Choose one:' % principal_name, choices)
        return PrincipalType[answer.upper()]
    else:
        return PrincipalType[list(results)[0].upper()]


def _get_resource_type(args):
    resource_id = args.resource
    if args.entity_type:
        ensure_resource_exists(resource_id, ResourceType.ENTITY_TYPE)
        return ResourceType.ENTITY_TYPE
    elif args.package:
        ensure_resource_exists(resource_id, ResourceType.PACKAGE)
        return ResourceType.PACKAGE
    elif args.plugin:
        ensure_resource_exists(resource_id, ResourceType.PLUGIN)
        return ResourceType.PLUGIN
    else:
        return _guess_resource_type(resource_id)


def _guess_resource_type(resource_id):
    results = dict()
    for resource_type in ResourceType:
        if resource_exists(resource_id, resource_type):
            results[resource_type.get_label()] = resource_id

    if len(results) == 0:
        raise McmdError('No resources found with id %s' % resource_id)
    elif len(results) > 1:
        choices = results.keys()
        answer = multi_choice('Multiple resources found for id %s. Choose one:' % resource_id, choices)
        return ResourceType.of_label(answer)
    else:
        return ResourceType.of_label(list(results)[0])
