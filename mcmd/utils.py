from pathlib import Path


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


def config_string_to_paths(config_string):
    """Strips and splits comma separated, multi-line configuration variables and converts them to Path objects."""
    clean_string = ''.join(config_string.split())
    paths = clean_string.split(',')
    return [Path(path_string) for path_string in paths]
