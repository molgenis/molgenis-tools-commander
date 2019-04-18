from mcmd.utils.errors import McmdError


class MolgenisOfflineError(McmdError):
    def __init__(self):
        self.message = "Can't connect to {}".format(config.url())

    def __str__(self):
        return repr(self.message)
