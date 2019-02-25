import mcmd.config.config as config
from mcmd import io
from mcmd.arguments import arguments
from mcmd.client.molgenis_client import ResourceType, post, ensure_resource_exists, one_resource_exists
from mcmd.command import command
from mcmd.io import highlight
from mcmd.utils.errors import McmdError


# =========
# Arguments
# =========

@arguments('enable')
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
                                type=str,
                                help='The bootstrap theme you want to enable, specify the name with or without '
                                     '(.min).css and with or without bootstrap- prefix.')


# =======
# Methods
# =======

@command
def enable_rls(args):
    io.start('Enabling row level security on entity type %s' % highlight(args.entity))

    ensure_resource_exists(args.entity, ResourceType.ENTITY_TYPE)
    post(config.api('rls'), data={'id': args.entity,
                                  'rlsEnabled': True})


@command
def enable_theme(args):
    """
    enable_theme enables a bootstrap theme
    :param args: commandline arguments containing the id of the theme (without .css)
    :exception McmdError: when applying the theme fails
    :return None
    """
    theme = args.theme.replace('.css', '').replace('.min', '')
    io.start('Applying theme {}'.format(highlight(theme)))
    # Resource can be bootstrap-name.min.css (if molgenis theme), or name.min.css (if uploaded .min.css), or
    # name.css (if uploaded as .css).
    if one_resource_exists([theme + '.min.css', theme + '.css', 'bootstrap-' + theme + '.min.css'], ResourceType.THEME):
        # Molgenis themes start with bootstrap- but this is stripped from the name in the theme manager
        try:
            post(config.api('set_theme'), theme)
        except:
            post(config.api('set_theme'), theme.split('bootstrap-')[1])
    else:
        raise McmdError(
            'Applying theme failed. No themes found containing {} in the name'.format(args.theme, 'sys_set_StyleSheet'))
