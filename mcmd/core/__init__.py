from mcmd.core import context_holder
from mcmd.core.context_holder import Context


def context() -> Context:
    return context_holder.get_context()
