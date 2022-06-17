import textwrap
from argparse import RawDescriptionHelpFormatter

from mcmd.commands._registry import arguments
from mcmd.core.command import command
from mcmd.core.compatibility import deprecated
from mcmd.core.errors import McmdError
from mcmd.in_out import in_out
from mcmd.in_out.in_out import highlight
from mcmd.molgenis import api
from mcmd.molgenis.client import post, put
from mcmd.molgenis.resources import one_resource_exists, ensure_resource_exists, ResourceType
from mcmd.molgenis.security import security


# =========
# Arguments
# =========

@arguments('enable')
def add_arguments(subparsers):
    p_enable = subparsers.add_parser('enable',
                                     help='enable resources and functionality',
                                     description="run 'mcmd enable rls -h' to view the help for those sub-commands")
    p_enable_subparsers = p_enable.add_subparsers(dest="type")

    p_enable_rls = p_enable_subparsers.add_parser('rls',
                                                  help='enables row level security on an entity type')
    p_enable_rls.set_defaults(func=enable_rls,
                              write_to_history=True)
    p_enable_rls.add_argument('entity',
                              type=str,
                              help="the entity type to secure")

    p_enable_theme = p_enable_subparsers.add_parser('theme',
                                                    help='enables a bootstrap theme (deprecated since 8.6)',
                                                    formatter_class=RawDescriptionHelpFormatter,
                                                    description=textwrap.dedent(
                                                        """
                                                        Enable a CSS theme. 

                                                        Deprecated since 8.6. The themes can now be configured in the 
                                                        Application settings. Read https://molgenis.gitbook.io/molgenis/configuration/guide-customize#style-theme
                                                        to learn more. 

                                                        Example usage:
                                                          mcmd enable theme theme3.css
                                                        """
                                                    )
                                                    )
    p_enable_theme.set_defaults(func=enable_theme,
                                write_to_history=True)
    p_enable_theme.add_argument('theme',
                                type=str,
                                help='the bootstrap theme you want to enable, specify the name with or without '
                                     '(.min).css and with or without bootstrap- prefix.')

    p_enable_language = p_enable_subparsers.add_parser('language',
                                                       help='enables a language')
    p_enable_language.set_defaults(func=enable_language,
                                   write_to_history=True)
    p_enable_language.add_argument('language',
                                   type=str,
                                   help="the language you want to enable, specified by the two letter code (e.g. 'en')")


# =======
# Methods
# =======

@command
def enable_rls(args):
    in_out.start('Enabling row level security on entity type %s' % highlight(args.entity))

    ensure_resource_exists(args.entity, ResourceType.ENTITY_TYPE)
    security.enable_row_level_security(args.entity)


@command
@deprecated(since='8.6.0',
            action='Enabling themes',
            info="Themes can be activated in the app settings now. Use the 'set' command to set the 'legacy_theme_url' "
                 "and 'theme_url'. Read https://molgenis.gitbook.io/molgenis/configuration/guide-customize#style-theme"
                 " to learn more.")
def enable_theme(args):
    """
    enable_theme enables a bootstrap theme
    :param args: commandline arguments containing the id of the theme (without .css)
    :exception McmdError: when applying the theme fails
    :return None
    """
    theme = args.theme.replace('.css', '').replace('.min', '')
    in_out.start('Applying theme {}'.format(highlight(theme)))
    # Resource can be bootstrap-name.min.css (if molgenis theme), or name.min.css (if uploaded .min.css), or
    # name.css (if uploaded as .css).
    if one_resource_exists([theme + '.min.css', theme + '.css', 'bootstrap-' + theme + '.min.css'], ResourceType.THEME):
        # Molgenis themes start with bootstrap- but this is stripped from the name in the theme manager
        try:
            post(api.set_theme(), data=theme)
        except:
            post(api.set_theme(), data=theme.split('bootstrap-')[1])
    else:
        raise McmdError(
            'Applying theme failed. No themes found containing {} in the name'.format(args.theme, 'sys_set_StyleSheet'))


@command
def enable_language(args):
    in_out.start('Enabling language {}'.format(highlight(args.language)))
    url = api.rest1('sys_Language/{}/active'.format(args.language))
    put(url, 'true')
