class ArgumentError(Exception):
    """Raise when a custom argument rule doesn't pass validation."""
    pass


class McmdError(Exception):
    """General error. Raise when something goes wrong during execution of a command."""

    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
