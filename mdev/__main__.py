import logging

from mdev.arguments import parse_args
from mdev.configuration import get_config


def main():
    logging.basicConfig(format='%(message)s', level=logging.INFO)

    config = get_config()
    args = parse_args()
    args.func(args, config)


if __name__ == '__main__':
    main()
