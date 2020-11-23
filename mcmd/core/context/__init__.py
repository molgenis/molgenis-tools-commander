"""
All interactions with preset locations on the file system should go through a Context object. See the 'Context' class
in the 'base_context' module for more information, and see the 'HomeContext' class in the 'home_context' module for the
default implementation.

The current context should be retrieved by using the package method in this file.
"""

from mcmd.core.context import _context_holder
from mcmd.core.context.base_context import Context


def context() -> Context:
    return _context_holder.get_context()
