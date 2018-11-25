"""
Enables or disables row level security on an entity type. Enables by default to prevent accidental removal of row level
security on important data. Will disable when the --disable flag is used.
"""

from mdev import io
from mdev.client.molgenis_client import post, login, resource_exists, ResourceType
from mdev.config.config import config
from mdev.io import highlight
from mdev.utils import MdevError


# =========
# Arguments
# =========

def arguments(subparsers):
    p_rls = subparsers.add_parser('rls',
                                  help='Enables row level security on an entity type. Can be disabled by using the'
                                       '--disabled flag.')
    p_rls.set_defaults(func=rls,
                       write_to_history=True)
    p_rls.add_argument('entity',
                       type=str,
                       help='The id of the entity type to enable/disable row level security for.')
    p_rls.add_argument('--disable', '-d',
                       action='store_true',
                       help='Disables row level security.')


# =======
# Methods
# =======

def rls(args):
    action_str = 'Enabling'
    if args.disable:
        action_str = 'Disabling'

    io.start('%s row level security on entity type %s' % (action_str, highlight(args.entity)))

    login(args)
    if not resource_exists(args.entity, ResourceType.ENTITY_TYPE):
        raise MdevError("Entity type %s doesn't exist" % args.entity)
    post(config().get('api', 'rls'), data={'id': args.entity,
                                           'rlsEnabled': not args.disable})
