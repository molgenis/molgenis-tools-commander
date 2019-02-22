class McmdError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class ConfigError(McmdError):
    def __init__(self, message):
        self.message = "There's an error in the configuration file: {}".format(message)

    def __str__(self):
        return repr(self.message)
