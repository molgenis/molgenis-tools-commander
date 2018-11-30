from pathlib import Path


class MdevError(Exception):
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
    """Strips and splits comma separated, multi-line configuration variables and converts them to Paths objects."""
    clean_string = ''.join(config_string.split())
    paths = clean_string.split(',')
    return [Path(path_string) for path_string in paths]


def is_true_or_false(boolean_like_value):
    truthy = ['true', '1', 't', 'y', 'yes', 'yeah', 'yup', 'certainly', 'uh-huh', 'sure', 'yep', 'yush']
    falsy = ['no', '0', 'nope', 'n', 'never', 'not', 'false', 'f']
    value = str(boolean_like_value.lower())
    if value in truthy:
        return True
    elif value in falsy:
        return False
    else:
        return None
