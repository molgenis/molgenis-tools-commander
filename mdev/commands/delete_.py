"""
Deletes an entityType or rows fo a given entityType.
"""

from mdev import io
from mdev.client.molgenis_client import delete, delete_data, login, resource_exists, ResourceType
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import MdevError

config = get_config()


def delete_(args):
    """
    delete_ deletes specified entityTypes or rows
    :param args: commandline arguments
    :return: None
    :exception: MdevError: when the entityType you try to delete (from) does not exist
    """
    login(args)

    if not resource_exists(args.entityType, ResourceType.ENTITY_TYPE):
        raise MdevError("Entity type {} doesn't exist".format(args.entityType))

    if args.data:
        _delete_data(args)
    else:
        _delete_entity_type(args)


def _delete_data(args):
    """
    _delete_data deletes rows from a entityType
    :param args: commandline arguments containing the entityType to delete from and the id's of the rows to remove
    :return: None
    """
    io.start('Deleting rows from entityType: {}'.format(highlight(args.entityType)))
    url = '{}{}'.format(config.get('api', 'rest2'), args.entityType)
    data = args.data.split(',')
    delete_data(url, data)


def _delete_entity_type(args):
    """
    _delete_entity_type deletes the specified entityType doing a delete request
    :param args: commandline arguments containing the entityType to delete
    :return: None
    """
    io.start('Deleting entityType: {}'.format(highlight(args.entityType)))
    url = '{}{}/meta'.format(config.get('api', 'rest1'), args.entityType)
    delete(url)
