"""
Deletes an entityType or data from an entityType.
"""
import mcmd.config.config as config
from mcmd import io
from mcmd.arguments import arguments
from mcmd.client.molgenis_client import delete, delete_data, ensure_resource_exists, ResourceType
from mcmd.command import command
from mcmd.io import highlight


# =========
# Arguments
# =========

@arguments('delete')
def arguments(subparsers):
    p_delete = subparsers.add_parser('delete',
                                     help='Delete entities or data',
                                     description="Run 'mcmd delete entity -h' or 'mcmd delete data -h' to view the help"
                                                 " for those sub-commands")
    p_delete.add_argument('--force', '-f',
                          action='store_true',
                          help="Does your delete action without asking if you know it for sure")
    p_delete_subparsers = p_delete.add_subparsers(dest="type")
    p_delete_entity = p_delete_subparsers.add_parser('entity',
                                                     help='Delete an entity(type)')
    p_delete_entity.add_argument('entity_type',
                                 type=str,
                                 metavar='ID',
                                 help="The ID of the entity type you want to delete")
    p_delete_entity.set_defaults(func=delete_entity,
                                 write_to_history=True)
    p_delete_data = p_delete_subparsers.add_parser('data',
                                                   help='Delete data from an entity(type)')
    p_delete_data.add_argument('entity_type',
                               metavar='ID',
                               type=str,
                               help="The ID of the entity type you want to delete all data from")
    p_delete_data.set_defaults(func=delete_all_data,
                               write_to_history=True)


# =======
# Methods
# =======

@command
def delete_all_data(args):
    ensure_resource_exists(args.entity_type, ResourceType.ENTITY_TYPE)
    if args.force or (not args.force and io.confirm(
            'Are you sure you want to remove all data from entity: {}?'.format(args.entity_type))):
        _delete_all_data(args.entity_type)


@command
def delete_entity(args):
    ensure_resource_exists(args.entity_type, ResourceType.ENTITY_TYPE)
    if args.force or (not args.force and io.confirm(
            'Are you sure you want to remove the complete entity: {}?'.format(args.entity_type))):
        _delete_entity_type(args.entity_type)


def _delete_row(entity, row):
    url = '{}{}'.format(config.api('rest2'), entity)
    delete_data(url, [row])


def _delete_all_data(entity):
    io.start('Deleting all data from entity {}'.format(highlight(entity)))
    url = '{}{}'.format(config.api('rest1'), entity)
    delete(url)


def _delete_entity_type(entity):
    io.start('Deleting entity {}'.format(highlight(entity)))
    _delete_row('sys_md_EntityType', entity)
