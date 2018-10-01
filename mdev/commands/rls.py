"""
Enables or disables row level security on an entity type. Enables by default to prevent accidental removal of row level
security on important data. Will disable when the --disable flag is used.
"""

from mdev import io
from mdev.client.molgenis_client import post, login, resource_exists, ResourceType
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import MdevError

config = get_config()


def rls(args):
    action_str = 'Enabling'
    if args.disable:
        action_str = 'Disabling'

    io.start('%s row level security on entity type %s' % (action_str, highlight(args.entity)))

    login(args)
    if not resource_exists(args.entity, ResourceType.ENTITY_TYPE):
        raise MdevError("Entity type %s doesn't exist" % args.entity)
    post(config.get('api', 'rls'), data={'id': args.entity,
                                         'rlsEnabled': not args.disable})
