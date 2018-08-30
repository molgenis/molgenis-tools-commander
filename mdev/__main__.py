from .arguments import parse_args
from configparser import ConfigParser
from pkg_resources import resource_string

import os


def main():
    args = parse_args()

    filename = resource_string('config', 'config.ini')
    if os.path.isfile(filename):
        config_parser = ConfigParser()
        config_parser.read(filename)
        print(config_parser.sections())
        username = config_parser.get('auth', 'username')
        password = config_parser.get('auth', 'password')
        print(username, password)
        args.func(args)
    else:
        print("ini not found")

if __name__ == '__main__':
    main()
