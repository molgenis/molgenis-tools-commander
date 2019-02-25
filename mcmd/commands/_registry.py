"""
Each command's argument adder is registered here.
"""

_ARGUMENT_ADDER_REGISTRY = dict()


def get_argument_adders():
    return [func for name, func in sorted(_ARGUMENT_ADDER_REGISTRY.items())]


def arguments(command_name):
    """Command argument adder registration decorator."""

    def decorator(func):
        _ARGUMENT_ADDER_REGISTRY[command_name] = func
        return func

    return decorator
