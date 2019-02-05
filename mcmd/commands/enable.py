import mcmd.config.config as config
from mcmd import io
from mcmd.client.molgenis_client import login, ResourceType, post, ensure_resource_exists
from mcmd.io import highlight
from mcmd.utils import McmdError


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

    p_enable_theme = p_enable_subparsers.add_parser('theme',
                                                    help='Enables the bootstrap theme which changes the styling of your'
                                                         ' MOLGENIS')
    p_enable_theme.set_defaults(func=enable_theme,
                                write_to_history=True)
    p_enable_theme.add_argument('theme',
                                metavar='THEME',
                                type=str,
                                help='The bootstrap theme you want to enable (without .css)')


# =======
# Methods
# =======

@login
def enable_rls(args):
    io.start('Enabling row level security on entity type %s' % highlight(args.entity))

    ensure_resource_exists(args.entity, ResourceType.ENTITY_TYPE)
    post(config.api('rls'), data={'id': args.entity,
                                  'rlsEnabled': True})


@login
def enable_theme(args):
    """
    enable_theme enables a bootstrap theme
    :param args: commandline arguments containing the id of the theme (without .css)
    :exception McmdError: when applying the theme fails
    :return None
    """
    io.start('Applying theme {}'.format(highlight(args.theme)))
    try:
        post(config.api('set_theme'), args.theme)
    except McmdError:
        raise McmdError(
            'Applying theme failed. Does theme [{}] exist in the [{}] table?'.format(args.theme, 'sys_set_StyleSheet'))
