"""
Houses the @arguments decorator, which registers each command's arguments.
"""
from collections import defaultdict

from mcmd.core.command import CommandType

_ARGUMENT_ADDER_REGISTRY = defaultdict(dict)


def get_argument_adders(type_: CommandType):
    return [func for name, func in sorted(_ARGUMENT_ADDER_REGISTRY[type_].items())]


def get_command_names(type_: CommandType):
    return [name for name, func in sorted(_ARGUMENT_ADDER_REGISTRY[type_].items())]


def arguments(command_name, type_=CommandType.STANDARD):
    """Command argument adder registration decorator."""

    def decorator(func):
        _ARGUMENT_ADDER_REGISTRY[type_][command_name] = func
        return func

    return decorator
