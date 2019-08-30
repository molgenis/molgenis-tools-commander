from urllib.parse import urljoin

import mcmd.io.ask
import mcmd.molgenis.client as client
from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.io import io
from mcmd.io.io import highlight
from mcmd.molgenis import api
from mcmd.molgenis.resources import detect_resource_type, ensure_resource_exists, ResourceType


# =========
# Arguments
# =========


@arguments('delete')
def add_arguments(subparsers):
    p_delete = subparsers.add_parser('delete',
                                     help='delete resources')
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

    p_delete_options = p_delete.add_mutually_exclusive_group()
    p_delete_options.add_argument('--data',
                                  action='store_true',
                                  help='Use in conjunction with --entity-type to only delete the rows of the entity '
                                       'type')
    p_delete_options.add_argument('--attribute',
                                  metavar='NAME',
                                  type=str,
                                  help='Use in conjunction with --entity-type to only delete an attribute of the '
                                       'entity type')
    p_delete_options.add_argument('--contents',
                                  action='store_true',
                                  help='Use in conjunction with --package to only delete the contents of the package')

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
        if args.data:
            _delete_entity_type_data(args)
        elif args.attribute:
            _delete_entity_type_attribute(args)
        else:
            _delete_entity_type(args)
    elif resource_type is ResourceType.PACKAGE:
        if args.contents:
            _delete_package_contents(args)
        else:
            _delete_package(args)
    elif resource_type is ResourceType.GROUP:
        _delete_group(args)


def _delete_entity_type(args):
    if args.force or (not args.force and mcmd.io.ask.confirm(
            'Are you sure you want to delete entity type {} including its data?'.format(args.resource))):
        io.start('Deleting entity type {}'.format(highlight(args.resource)))
        _delete_rows(ResourceType.ENTITY_TYPE.get_entity_id(), [args.resource])


def _delete_entity_type_data(args):
    if args.force or (not args.force and mcmd.io.ask.confirm(
            'Are you sure you want to delete all data in entity type {}?'.format(args.resource))):
        io.start('Deleting all data from entity {}'.format(highlight(args.resource)))
        client.delete(api.rest1(args.resource))


def _delete_entity_type_attribute(args):
    if args.force or (not args.force and mcmd.io.ask.confirm(
            'Are you sure you want to delete attribute {} of entity type {}?'.format(args.attribute, args.resource))):
        io.start('Deleting attribute {} of entity {}'.format(highlight(args.attribute), highlight(args.resource)))
        response = client.get(api.rest2('sys_md_Attribute'),
                              params={
                                  'q': 'entity=={};name=={}'.format(args.resource,
                                                                    args.attribute)
                              })
        attribute_id = response.json()['items'][0]['id']
        client.delete(api.rest2('sys_md_Attribute/{}'.format(attribute_id)))


def _delete_package(args):
    if args.force or (not args.force and mcmd.io.ask.confirm(
            'Are you sure you want to delete package {} and all of its contents?'.format(args.resource))):
        io.start('Deleting package {}'.format(highlight(args.resource)))
        _delete_rows(ResourceType.PACKAGE.get_entity_id(), [args.resource])


def _delete_package_contents(args):
    if args.force or (not args.force and mcmd.io.ask.confirm(
            'Are you sure you want to delete the contents of package {}?'.format(args.resource))):
        io.start('Deleting contents of package {}'.format(highlight(args.resource)))
        _delete_entity_types_in_package(args.resource)
        _delete_packages_in_package(args.resource)


def _delete_entity_types_in_package(package_id):
    response = client.get(api.rest2(ResourceType.ENTITY_TYPE.get_entity_id()),
                          params={
                              'attrs': 'id',
                              'q': 'package==' + package_id
                          })
    entity_ids = [entity_type['id'] for entity_type in response.json()['items']]
    if len(entity_ids) > 0:
        _delete_rows(ResourceType.ENTITY_TYPE.get_entity_id(), entity_ids)


def _delete_packages_in_package(package_id):
    response = client.get(api.rest2(ResourceType.PACKAGE.get_entity_id()),
                          params={
                              'attrs': 'id',
                              'q': 'parent==' + package_id
                          })
    package_ids = [entity_type['id'] for entity_type in response.json()['items']]
    if len(package_ids) > 0:
        _delete_rows(ResourceType.PACKAGE.get_entity_id(), package_ids)


def _delete_group(args):
    if args.force or (not args.force and mcmd.io.ask.confirm(
            'Are you sure you want to delete group {}?'.format(args.resource))):
        io.start('Deleting group {}'.format(highlight(args.resource)))
        client.delete(urljoin(api.group(), args.resource))


def _delete_rows(entity_type, rows):
    client.delete_data(api.rest2(entity_type), rows)


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
        return detect_resource_type(resource_id, [ResourceType.ENTITY_TYPE, ResourceType.PACKAGE, ResourceType.GROUP])
