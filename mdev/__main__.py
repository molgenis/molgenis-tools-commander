import logging

from mdev.arguments import parse_args
from mdev.configuration import load_config


def main():
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    load_config()
    args = parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
