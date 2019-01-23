import mcmd.config.config as config
from mcmd import io
from mcmd.client.molgenis_client import login, ResourceType, post, ensure_resource_exists
from mcmd.io import highlight


# =========
# Arguments
# =========


def arguments(subparsers):
    p_enable = subparsers.add_parser('enable',
                                     help='Enable resources/functionality',
                                     description="Run 'mcmd enable rls -h' to view the help for those sub-commands")
    p_enable_subparsers = p_enable.add_subparsers(dest="type")

    p_enable_rls = p_enable_subparsers.add_parser('rls',
                                                  help='Enables row level security on an entity type')
    p_enable_rls.set_defaults(func=enable_rls,
                              write_to_history=True)
    p_enable_rls.add_argument('entity',
                              type=str,
                              help="The entity type to secure")


# =======
# Methods
# =======

@login
def enable_rls(args):
    io.start('Enabling row level security on entity type %s' % highlight(args.entity))

    ensure_resource_exists(args.entity, ResourceType.ENTITY_TYPE)
    post(config.api('rls'), data={'id': args.entity,
                                  'rlsEnabled': True})
