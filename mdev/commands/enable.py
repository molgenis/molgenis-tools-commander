"""
Enables themes (for now)
"""

from mdev import io
from mdev.client.molgenis_client import login, post
from mdev.config.config import get_config
from mdev.io import highlight
from mdev.utils import MdevError

config = get_config()


def enable_theme(args):
    """
    enable_theme enables a bootstrap theme
    :param args: commandline arguments containing the id of the theme (without .css)
    :return: MdevError: when applying the theme fails
    """
    login(args)
    io.start('Applying theme: {}'.format(highlight(args.theme)))
    try:
        post(config.get('api', 'set_theme'), args.theme)
    except MdevError:
        raise MdevError('Applying theme failed. Does {} exist in the {} table?'.format(args.theme, 'sys_set_StyleSheet'))
