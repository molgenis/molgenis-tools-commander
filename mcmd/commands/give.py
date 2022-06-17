"""
Give a principal (a user or a group) some permission on a resource (a package, entity type, plugin or row). Unless
specified by the user, the give command will try to figure out the principal- and resource types itself. If a resource
or principal doesn't exist, the program will terminate.
"""
import textwrap
from argparse import RawDescriptionHelpFormatter

from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.core.compatibility import version
from mcmd.core.errors import McmdError
from mcmd.in_out import in_out
from mcmd.in_out.in_out import highlight
from mcmd.molgenis.principals import PrincipalType, get_principal_type_from_args
from mcmd.molgenis.resources import detect_resource_type, ensure_resource_exists, ResourceType
from mcmd.molgenis.security import security
from mcmd.molgenis.security.permission import Permission
from mcmd.molgenis.version import get_version


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
                                       
                                       If you want to remove a permission, use the 'none' permission.

                                       Note: since MOLGENIS 8.3 role names are case sensitive and need to be typed 
                                       exactly as-is. (Before 8.3 all role names will be upper cased automatically). 

                                       example usage:
                                         mcmd give john read dataset
                                         mcmd give --user john read --entity-type dataset
                                         
                                         mcmd give group_EDITOR write dataexplorer
                                         mcmd give --role group_EDITOR write --plugin dataexplorer
                                         
                                         mcmd give john edit dataset --entity biobank1
                                         mcmd give --user john edit --entity-type dataset --entity biobank1
                                       """
                                   ))
    p_give.set_defaults(func=give,
                        write_to_history=True)
    p_give_resource = p_give.add_mutually_exclusive_group()
    p_give_resource.add_argument('--entity-type', '-e',
                                 action='store_true',
                                 help='flag to specify that the resource is an entity type (assumed when using '
                                      '--entity)')
    p_give_resource.add_argument('--package', '-p',
                                 action='store_true',
                                 help='flag to specify that the resource is a package')
    p_give_resource.add_argument('--plugin', '-pl',
                                 action='store_true',
                                 help='flag to specify that the resource is a plugin')
    p_give_receiver = p_give.add_mutually_exclusive_group()
    p_give.add_argument('--entity', '-E',
                        metavar='ENTITY_ID',
                        help='use in conjunction with --entity-type to give permissions for a row')
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
# Methods
# =======

@command
def give(args):
    _validate_args(args)

    permission = Permission[args.permission.upper()]

    principal_type = get_principal_type_from_args(args, principal_name=args.receiver)

    if args.entity:
        _grant_rls(principal_type=principal_type,
                   principal_name=args.receiver,
                   entity_type_id=args.resource,
                   entity_id=args.entity,
                   permission=permission)
    else:
        resource_type = _get_resource_type(args)
        _grant(principal_type=principal_type,
               principal_name=args.receiver,
               resource_type=resource_type,
               entity_type_id=args.resource,
               permission=permission)


@version('7.0.0')
def _validate_args(args):
    if args.entity:
        raise McmdError(
            "Giving row level permissions is only possible since MOLGENIS 8.1.1 (you are using {})".format(
                get_version()))


# noinspection PyUnusedLocal
@version('8.1.1')
def _validate_args(args):
    pass


def _grant(principal_type: PrincipalType, principal_name: str, resource_type: ResourceType, entity_type_id: str,
           permission: Permission):
    in_out.start('Giving %s %s permission to %s on %s %s' % (principal_type.value,
                                                         highlight(principal_name),
                                                         highlight(permission.value),
                                                         resource_type.get_label().lower(),
                                                         highlight(entity_type_id)))

    security.grant_permission(principal_type, principal_name, resource_type, entity_type_id, permission)


def _grant_rls(principal_type: PrincipalType, principal_name: str, entity_type_id: str,
               entity_id: str, permission: Permission):
    in_out.start('Giving %s %s permission to %s on row %s of entity type %s' % (principal_type.value,
                                                                            highlight(principal_name),
                                                                            highlight(permission.value),
                                                                            highlight(entity_id),
                                                                            highlight(entity_type_id)))

    security.grant_row_permission(principal_type, principal_name, entity_type_id, entity_id, permission)


def _get_resource_type(args):
    # The permission manager doesn't check if the resources actually exist so we need to do that ourselves

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
