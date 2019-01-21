import mcmd.config.config as config
from mcmd import io
from mcmd.io import highlight


# =========
# Arguments
# =========


def arguments(subparsers):
    p_config = subparsers.add_parser('config',
                                     help='Change the configuration of Molgenis Commander')
    p_config_subparsers = p_config.add_subparsers(dest="type")

    p_config_set = p_config_subparsers.add_parser('set',
                                                  help='Set values in the configuration file')

    p_config_set_subparsers = p_config_set.add_subparsers()
    p_config_set_host = p_config_set_subparsers.add_parser('host',
                                                           help='Select a host')
    p_config_set_host.set_defaults(func=config_set_host,
                                   write_to_history=False)
    p_config_set_host.add_argument('url',
                                   nargs='?',
                                   help='The URL of the host (Optional)')


# =======
# Methods
# =======

def config_set_host(args):
    if args.url:
        url = args.url
    else:
        auths = config.get('host', 'auth')
        urls = [auth['url'] for auth in auths]
        url = io.multi_choice('Choose the host you want to select:', urls)

    io.start("Selecting host {}".format(highlight(url)))
    config.set_host(url)
