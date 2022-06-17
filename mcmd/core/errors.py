from mcmd.config import config


class ApiError(Exception):
    pass


class McmdError(Exception):
    def __init__(self, message, info: str = None):
        """
        :param message: the error message to show
        :param info: an optional info message that will be shown after the error
        """
        self.message = message
        self.info = info

    def __str__(self):
        return repr(self.message)


class ScriptError(McmdError):
    def __init__(self, message, line: int, info: str = None):
        super().__init__(message, info)
        self.line = line

    @classmethod
    def from_error(cls, error: McmdError, line: int):
        return cls(error.message, line, error.info)


class ConfigError(McmdError):
    def __init__(self, message):
        super().__init__(message="There's an error in the configuration file: {}".format(message))


class MolgenisOfflineError(McmdError):
    def __init__(self):
        super().__init__(message="Can't connect to {}".format(config.url()))
