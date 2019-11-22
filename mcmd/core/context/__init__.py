from mcmd.core.context import _context_holder
from mcmd.core.context.base_context import Context


def context() -> Context:
    return _context_holder.get_context()


def set_context(new_context: Context):
    _context_holder.set_context(new_context)
