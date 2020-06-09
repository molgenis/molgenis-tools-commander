class ArgumentSyntaxError(Exception):
    def __init__(self, message: str, usage: str):
        super().__init__(message)
        self._usage = usage

    @property
    def usage(self):
        return self._usage
