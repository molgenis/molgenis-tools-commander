import argparse
from io import StringIO

from mcmd.args.errors import ArgumentSyntaxError


class RaisingArgumentParser(argparse.ArgumentParser):
    """
    When an error occurs, the default ArgumentParser prints the usage + error message directly to stderr and then exits
    the program. This subclass raises an ArgumentSyntaxError instead so that the caller can decide what to do when
    parsing fails.
    """

    def error(self, message):
        message = self.prog + ': ' + message
        raise ArgumentSyntaxError(message=message, usage=self.get_usage_as_string())

    def get_usage_as_string(self):
        with StringIO() as usage_io:
            self.print_usage(usage_io)
            return usage_io.getvalue()
