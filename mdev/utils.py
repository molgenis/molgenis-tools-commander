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


def config_string_to_list(config_string):
    """Strips and splits comma separated, multi-line configuration variables."""
    clean_string = ''.join(config_string.split())
    strings = clean_string.split(',')
    map(str.strip, strings)
    return strings