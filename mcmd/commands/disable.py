import mcmd.config.config as config
from mcmd import io
from mcmd.client.molgenis_client import ResourceType, post, ensure_resource_exists
from mcmd.command import command
from mcmd.io import highlight


# =========
# Arguments
# =========


def arguments(subparsers):
    p_disable = subparsers.add_parser('disable',
                                      help='Disable resources/functionality',
                                      description="Run 'mcmd disable rls -h' to view the help for those sub-commands")
    p_disable_subparsers = p_disable.add_subparsers(dest="type")

    p_disable_rls = p_disable_subparsers.add_parser('rls',
                                                    help='Disables row level security on an entity type')
    p_disable_rls.set_defaults(func=enable_rls,
                               write_to_history=True)
    p_disable_rls.add_argument('entity',
                               type=str,
                               help="The entity type to remove the row level security from")


# =======
# Methods
# =======

@command
def enable_rls(args):
    if not io.confirm('Are you sure you want to disable row level security on %s?' % args.entity):
        return

    io.start('Disabling row level security on entity type %s' % highlight(args.entity))

    ensure_resource_exists(args.entity, ResourceType.ENTITY_TYPE)
    post(config.api('rls'), data={'id': args.entity,
                                  'rlsEnabled': False})
