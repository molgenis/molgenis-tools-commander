from urllib.parse import urljoin

from mcmd import io
from mcmd.client.molgenis_client import ResourceType, ensure_resource_exists, delete_data, delete as client_delete
from mcmd.command import command
from mcmd.commands._registry import arguments
from mcmd.config import config
from mcmd.io import highlight
from mcmd.utils.types import guess_resource_type


# =========
# Arguments
# =========


@arguments('delete')
def add_arguments(subparsers):
    p_delete = subparsers.add_parser('delete',
                                     help='Delete resources')
    p_delete.set_defaults(func=delete,
                          write_to_history=True)
    p_delete_resource = p_delete.add_mutually_exclusive_group()
    p_delete_resource.add_argument('--entity-type', '-e',
                                   action='store_true',
                                   help='Flag to specify that the resource is an entity type')
    p_delete_resource.add_argument('--package', '-p',
                                   action='store_true',
                                   help='Flag to specify that the resource is a package')
    p_delete_resource.add_argument('--group', '-g',
                                   action='store_true',
                                   help='Flag to specify that the resource is a group')
    p_delete.add_argument('--force', '-f',
                          action='store_true',
                          help='Forces the delete action without asking for confirmation')
    p_delete.add_argument('resource',
                          type=str,
                          help='The identifier of the resource to delete')


# =======
# Methods
# =======


@command
def delete(args):
    resource_type = _get_resource_type(args)
    if resource_type is ResourceType.ENTITY_TYPE:
        _delete_entity_type(args)
    elif resource_type is ResourceType.PACKAGE:
        _delete_package(args)
    elif resource_type is ResourceType.GROUP:
        _delete_group(args)


def _delete_entity_type(args):
    if args.force or (not args.force and io.confirm(
            'Are you sure you want to delete entity type {} including its data?'.format(args.resource))):
        io.start('Deleting entity type {}'.format(highlight(args.resource)))
        _delete_row('sys_md_EntityType', args.resource)


def _delete_package(args):
    if args.force or (not args.force and io.confirm(
            'Are you sure you want to delete package {} and all of its contents?'.format(args.resource))):
        io.start('Deleting package {}'.format(highlight(args.resource)))
        _delete_row('sys_md_Package', args.resource)


def _delete_group(args):
    if args.force or (not args.force and io.confirm(
            'Are you sure you want to delete group {}?'.format(args.resource))):
        io.start('Deleting group {}'.format(highlight(args.resource)))
        client_delete(urljoin(config.get('group'), args.resource))


def _delete_row(entity_type, row):
    url = '{}{}'.format(config.api('rest2'), entity_type)
    delete_data(url, [row])


def _get_resource_type(args):
    resource_id = args.resource
    if args.entity_type:
        ensure_resource_exists(resource_id, ResourceType.ENTITY_TYPE)
        return ResourceType.ENTITY_TYPE
    elif args.package:
        ensure_resource_exists(resource_id, ResourceType.PACKAGE)
        return ResourceType.PACKAGE
    elif args.group:
        ensure_resource_exists(resource_id, ResourceType.GROUP)
        return ResourceType.GROUP
    else:
        return guess_resource_type(resource_id, [ResourceType.ENTITY_TYPE, ResourceType.PACKAGE, ResourceType.GROUP])
