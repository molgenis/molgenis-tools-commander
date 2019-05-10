""""This module uses internals of the argparse library to realise functionality that is not (yet) supported."""

import argparse
import textwrap

from mcmd.commands import get_command_names
from mcmd.core.command import CommandType


# noinspection PyProtectedMember
class GroupedHelpFormatter(argparse.RawTextHelpFormatter):
    """Grouping commands is not supported in argparse. This custom help formatter inserts
    headers between the groups."""

    def __init__(self, *args, **kwargs):
        super(GroupedHelpFormatter, self).__init__(*args, **kwargs)
        self._standard_commands = get_command_names(CommandType.STANDARD)
        self._local_commands = get_command_names(CommandType.LOCAL)
        self._meta_commands = get_command_names(CommandType.META)

    def _get_group_header(self, name):
        """Check if this command is the first in one of the groups. If so, return the header for that group."""
        if self._standard_commands[0] == name:
            return textwrap.dedent('''\
                            MOLGENIS commands:
                            ''')
        elif len(self._local_commands) > 0 and self._local_commands[0] == name:
            return textwrap.dedent('''
                            Local commands:
                            ''')
        elif self._meta_commands[0] == name:
            return textwrap.dedent('''
                            meta commands:
                            ''')
        else:
            return False

    def _format_action(self, action):
        """Overrides RawTextHelpFormatter._format_action"""
        help_string = super(GroupedHelpFormatter, self)._format_action(action)

        header = self._get_group_header(action.dest)
        if header:
            help_string = header + help_string
        return help_string


# noinspection PyProtectedMember
def list_subcommands_in_help(parser):
    """Adds a list of subcommands to a command's help string."""
    main_parser = [
        action for action in parser._actions
        if isinstance(action, argparse._SubParsersAction)][0]

    for command in main_parser._choices_actions:
        if command.dest in main_parser.choices:
            subcommands = [
                action for action in main_parser.choices[command.dest]._actions
                if isinstance(action, argparse._SubParsersAction)]
            if len(subcommands) == 0:
                continue
            else:
                subcommands = subcommands[0]

            subs = []
            for subcommand in subcommands._choices_actions:
                subs.append(subcommand.dest)

            command.help = '{}\r- subcommands: {}'.format(command.help,
                                                          ', '.join(subs))
