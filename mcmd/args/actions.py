import argparse

from mcmd.args._raising_parser import RaisingArgumentParser
from mcmd.args.errors import ArgumentSyntaxError


class ParseKeyValue(argparse.Action):
    """
    Parses key/value pairs, separated by an '=' sign. Returns a dictionary.
    Will parse the values 'true' and 'false' as booleans. As a consequence, string literals 'true' and 'false' are not
    supported.
    """

    def __call__(self, parser: RaisingArgumentParser, namespace, values, option_string=None):
        d = {}

        if values:
            for item in values:
                split_items = item.split("=", 1)

                if len(split_items) != 2:
                    raise ArgumentSyntaxError("Not a valid key/value pair: {}".format(item),
                                              parser.get_usage_as_string())

                key = split_items[0].strip()
                value = ParseKeyValue.__to_bool_or_str(split_items[1])

                d[key] = value

        setattr(namespace, self.dest, d)

    @staticmethod
    def __to_bool_or_str(value: str):
        if value == 'true':
            return True
        elif value == 'false':
            return False
        else:
            return value
