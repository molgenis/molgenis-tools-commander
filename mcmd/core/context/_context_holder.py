from typing import Optional

from mcmd.core.context.base_context import Context

_context: Optional[Context] = None


def set_context(new_context: Context):
    global _context
    _context = new_context


def get_context() -> Context:
    if _context is None:
        raise ValueError("context not set")
    else:
        return _context
