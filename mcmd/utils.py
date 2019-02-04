import os


class McmdError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


def upper_snake(string):
    """
    Transforms a string to uppercase snake style.
    E.g. 'lower-kebab-style' becomes 'LOWER_KEBAB_STYLE'.
    """
    return string.upper().replace('-', '_')


def lower_kebab(string):
    """
    Transforms a string to lowercase kebab style.
    E.g. 'SCREAMING_SNAKE' becomes 'screaming-snake'.
    """
    return string.lower().replace('_', '-')


def get_file_name_from_path(path):
    """
    get_file_name returns a file name from a path to the file
    :param path: path to the file (i.e. /Users/henk/Desktop/example.xlsx)
    :return: filename (i.e. example.xlsx)
    """
    return path.split(os.sep)[-1]
