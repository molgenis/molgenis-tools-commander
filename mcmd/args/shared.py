import argparse

_as_user_parser = argparse.ArgumentParser(add_help=False)
_as_user_parser.add_argument('--as-user',
                             type=str,
                             metavar='USER',
                             help="execute a command as a user")
_as_user_parser.add_argument('--with-password',
                             type=str,
                             metavar='PASSWORD',
                             help="the password to use when logging in --as-user")


def as_user_parser():
    return _as_user_parser
