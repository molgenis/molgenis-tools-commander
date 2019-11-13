"""
Every module in this package represents a command.

This package initialization makes every command module available for a global import:
'from mcmd.commands import *'.
"""

import glob
from os.path import dirname, basename, isfile

from mcmd.commands._registry import get_argument_adders
from mcmd.commands._registry import get_command_names

modules = glob.glob(dirname(__file__) + "/*.py")
__all__ = [basename(f)[:-3] for f in modules if isfile(f) and not f.startswith('_')]
