from mdev import io
from mdev.client.molgenis_client import login, ResourceType, post, ensure_resource_exists
from mdev.config.config import config
from mdev.io import highlight


# =========
# Arguments
# =========


def arguments(subparsers):
    p_add = subparsers.add_parser('enable',
                                  help='Enable resources/functionality',
                                  description="Run 'mdev enable rls -h' to view the help for those sub-commands")
    p_add_subparsers = p_add.add_subparsers(dest="type")

    p_add_group = p_add_subparsers.add_parser('rls',
                                              help='Enables row level security on an entity type')
    p_add_group.set_defaults(func=enable_rls,
                             write_to_history=True)
    p_add_group.add_argument('entity',
                             type=str,
                             help="The entity type to secure")


# =======
# Methods
# =======

@login
def enable_rls(args):
    io.start('Enabling row level security on entity type %s' % highlight(args.entity))

    ensure_resource_exists(args.entity, ResourceType.ENTITY_TYPE)
    post(config().get('api', 'rls'), data={'id': args.entity,
                                           'rlsEnabled': True})
