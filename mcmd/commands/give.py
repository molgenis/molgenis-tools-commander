"""
Give a principal (a user or a group) some permission on a resource (a package, entity type or plugin). Unless specified
by the user, the give command will try to figure out the principal- and resource types itself. If a resource or
principal doesn't exist, the program will terminate.
"""
import textwrap
from argparse import RawDescriptionHelpFormatter
from urllib.parse import urljoin

from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.core.errors import McmdError
from mcmd.io import io
from mcmd.io.io import highlight
from mcmd.molgenis import api
from mcmd.molgenis.client import post_form
from mcmd.molgenis.principals import PrincipalType, to_role_name, \
    get_principal_type_from_args
from mcmd.molgenis.resources import detect_resource_type, ensure_resource_exists, ResourceType


# =========
# Arguments
# =========


@arguments('give')
def add_arguments(subparsers):
    p_give = subparsers.add_parser('give',
                                   help='give permissions on resources to roles or users',
                                   formatter_class=RawDescriptionHelpFormatter,
                                   description=textwrap.dedent(
                                       """
                                       Give permissions on resources to roles or users. If you don't specify the 
                                       resource type (for example with --package or --plugin) or the receiver type 
                                       (--role or --user), the Commander will try to detect it on its own. 

                                       Note: since MOLGENIS 8.3 role names are case sensitive and need to be typed 
                                       exactly as-is. (Before 8.3 all role names will be upper cased automatically). 

                                       example usage:
                                         mcmd give john read dataset
                                         mcmd give --user john read --entity-type dataset
                                         
                                         mcmd give group_EDITOR write dataexplorer
                                         mcmd give --role group_EDITOR write --plugin dataexplorer
                                       """
                                   ))
    p_give.set_defaults(func=give,
                        write_to_history=True)
    p_give_resource = p_give.add_mutually_exclusive_group()
    p_give_resource.add_argument('--entity-type', '-e',
                                 action='store_true',
                                 help='flag to specify that the resource is an entity type')
    p_give_resource.add_argument('--package', '-p',
                                 action='store_true',
                                 help='flag to specify that the resource is a package')
    p_give_resource.add_argument('--plugin', '-pl',
                                 action='store_true',
                                 help='flag to specify that the resource is a plugin')
    p_give_receiver = p_give.add_mutually_exclusive_group()
    p_give_receiver.add_argument('--user', '-u',
                                 action='store_true',
                                 help='flag to specify that the receiver is a user')
    p_give_receiver.add_argument('--role', '-r',
                                 action='store_true',
                                 help='flag to specify that the receiver is a role')
    p_give.add_argument('receiver',
                        type=str,
                        help='the role (or user) to give the permission to')
    p_give.add_argument('permission',
                        choices=['none', 'writemeta', 'readmeta', 'write', 'edit', 'read', 'view', 'count'],
                        help='the permission type to give - synonyms are allowed (e.g. write/edit)')
    p_give.add_argument('resource',
                        type=str,
                        help='the resource to which permission is given')


# =======
# Globals
# =======


_PERMISSION_SYNONYMS = {'view': 'read',
                        'edit': 'write'}


# =======
# Methods
# =======

@command
def give(args):
    # Convert synonyms to correct permission type
    if args.permission in _PERMISSION_SYNONYMS:
        args.permission = _PERMISSION_SYNONYMS[args.permission]

    # The PermissionManagerController always gives 200 OK so we need to validate everything ourselves
    resource_type = _get_resource_type(args)
    principal_type = get_principal_type_from_args(args, principal_name=args.receiver)

    _grant(principal_type, args.receiver, resource_type, args.resource, args.permission)


def _grant(principal_type, principal_name, resource_type, identifier, permission):
    data = {'radio-' + identifier: permission}

    if principal_type == PrincipalType.USER:
        data['username'] = principal_name
    elif principal_type == PrincipalType.ROLE:
        principal_name = to_role_name(principal_name)
        data['rolename'] = principal_name
    else:
        raise McmdError('Unknown principal type: %s' % principal_type)

    io.start('Giving %s %s permission to %s on %s %s' % (principal_type.value,
                                                         highlight(principal_name),
                                                         highlight(permission),
                                                         resource_type.get_label().lower(),
                                                         highlight(identifier)))

    url = urljoin(api.permissions(), '{}/{}'.format(resource_type.get_resource_name(), principal_type.value))
    post_form(url, data)


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
        return detect_resource_type(resource_id, [ResourceType.ENTITY_TYPE, ResourceType.PACKAGE, ResourceType.PLUGIN])
